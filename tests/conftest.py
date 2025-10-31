"""
Pytest configuration and fixtures for LeanParanoia tests.
"""

import os
import json
import pytest
import subprocess
import shutil
import hashlib
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


TEST_DIR = Path(__file__).parent
LEAN_FILES = TEST_DIR / "lean_exploit_files"
TEMPLATE_DIR = TEST_DIR / "project_template"
BUILD_DIR = Path(".pytest_cache/LeanTestProject")
LEAN_FILES_HASH_MARKER = BUILD_DIR / ".lean_exploit_files_hash"
MATHLIB_BUILD_DIR = Path(".pytest_cache/MathlibBenchmark")
MATHLIB_TEMPLATE_DIR = TEST_DIR / "mathlib_project"
ROOT_DIR = TEST_DIR.parent


def compute_lean_exploit_files_hash() -> str:
    """Compute a stable hash of all Lean fixture files."""
    if not LEAN_FILES.exists():
        return "<none>"

    digest = hashlib.sha256()
    for lean_file in sorted(LEAN_FILES.rglob("*.lean")):
        relative = lean_file.relative_to(LEAN_FILES).as_posix().encode()
        digest.update(relative)
        digest.update(b"\0")
        digest.update(lean_file.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


@dataclass
class VerificationResult:
    """Result of verifying a theorem"""

    success: bool
    failures: Dict[str, List[str]]
    error_trace: Optional[str] = None

    @property
    def failed_tests(self) -> List[str]:
        return list(self.failures.keys())

    @property
    def errors(self) -> List[str]:
        combined: List[str] = []
        for messages in self.failures.values():
            combined.extend(messages)
        return combined


class Verifier:
    """Interface to LeanParanoia verifier"""

    def __init__(self, paranoia_path: Path, test_project_path: Path):
        self.paranoia_path = paranoia_path
        self.test_project_path = test_project_path

    def verify_theorem(
        self, module: str, theorem: str, config: Optional[Dict[str, Any]] = None
    ) -> VerificationResult:
        """
        Verify a theorem from the test project.

        Args:
            module: e.g., "LeanTestProject.Sorry.Direct"
            theorem: e.g., "exploit_theorem"
            config: Optional config overrides

        Returns:
            VerificationResult
        """
        # Build the full theorem name
        theorem_name = f"{module}.{theorem}"

        # Build command arguments
        cmd = ["lake", "env", str(self.paranoia_path), theorem_name]

        # Add config flags if provided
        if config:
            # Map config keys to their corresponding CLI flags
            flag_mappings = {
                "checkSorry": "--no-sorry",
                "checkMetavariables": "--no-metavariables",
                "checkUnsafe": "--no-unsafe",
                "checkAxioms": "--no-axioms",
                "checkExtern": "--no-extern",
                "checkConstructors": "--no-constructors",
                "checkRecursors": "--no-recursors",
                "enableReplay": "--no-replay",
                "checkOpaqueBodies": "--no-opaque-bodies",
                "checkSource": "--no-source-check",
            }

            # Add flags for disabled checks (default is True/enabled)
            for config_key, flag in flag_mappings.items():
                if not config.get(config_key, True):
                    cmd.append(flag)

            if "allowedAxioms" in config:
                axioms = ",".join(config["allowedAxioms"])
                cmd.extend(["--allowed-axioms", axioms])

            if "trustModules" in config and config["trustModules"]:
                modules = ",".join(config["trustModules"])
                cmd.extend(["--trust-modules", modules])

            if config.get("failFast", False):
                cmd.append("--fail-fast")

        # Run verification in the test project directory
        try:
            result = subprocess.run(
                cmd,
                cwd=self.test_project_path,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes for complex Mathlib theorems
            )

            raw_stdout = result.stdout.strip()
            raw_stderr = result.stderr.strip()

            # Try parsing the JSON payload emitted by the verifier
            json_payload = None
            for candidate in (raw_stdout, raw_stderr):
                if not candidate:
                    continue
                try:
                    json_payload = json.loads(candidate)
                    break
                except json.JSONDecodeError:
                    continue

            if json_payload is not None:
                success = bool(json_payload.get("success", False))
                failures_raw = json_payload.get("failures", {})
                failures = {
                    str(name): [str(msg) for msg in messages]
                    for name, messages in failures_raw.items()
                }
                error_trace = json_payload.get("errorTrace") or json_payload.get(
                    "error_trace"
                )
                return VerificationResult(
                    success=success,
                    failures=failures,
                    error_trace=error_trace if error_trace else None,
                )

            # Fallback to legacy text parsing for older verifier builds
            output = (raw_stdout + "\n" + raw_stderr).strip()
            success = result.returncode == 0

            failed: Dict[str, List[str]] = {}
            generic_errors: List[str] = []

            if "Failed tests:" in output:
                in_failed = False
                for line in output.split("\n"):
                    if "Failed tests:" in line:
                        in_failed = True
                        continue
                    if in_failed and line.strip().startswith("-"):
                        test_name = line.strip().lstrip("- ")
                        failed.setdefault(test_name, [])
                    elif in_failed and (line.strip() == "" or "Errors:" in line):
                        in_failed = False

            if "Errors:" in output:
                in_errors = False
                for line in output.split("\n"):
                    if "Errors:" in line:
                        in_errors = True
                        continue
                    if in_errors and line.strip():
                        if line.strip().startswith("Trace:"):
                            break
                        generic_errors.append(line.strip())

            if generic_errors:
                failed.setdefault("General", []).extend(generic_errors)

            return VerificationResult(
                success=success,
                failures=failed,
                error_trace=output if not success else None,
            )

        except subprocess.TimeoutExpired:
            return VerificationResult(
                success=False,
                failures={"Timeout": ["Verification timed out after 30 seconds"]},
            )
        except Exception as e:
            return VerificationResult(
                success=False,
                failures={"Error": [f"Error running verifier: {e}"]},
            )


@pytest.fixture(scope="session", autouse=True)
def setup_lean_test_project():
    """
    Generate Lean test project dynamically before running tests.

    Steps:
    1. Read lean-toolchain from root directory
    2. Create BUILD_DIR
    3. Copy lakefile.toml.template → BUILD_DIR/lakefile.toml
    4. Copy lean-toolchain from root
    5. Copy all files from tests/lean_exploit_files → BUILD_DIR/LeanTestProject/
    6. Generate LeanTestProject.lean with all imports
    7. Run lake update & lake build
    """

    # Check if BUILD_DIR exists and is up to date
    lean_toolchain_file = ROOT_DIR / "lean-toolchain"
    version_marker = BUILD_DIR / ".lean_version"

    current_hash = compute_lean_exploit_files_hash()

    if (
        BUILD_DIR.exists()
        and version_marker.exists()
        and LEAN_FILES_HASH_MARKER.exists()
    ):
        current_version = lean_toolchain_file.read_text().strip()
        cached_version = version_marker.read_text().strip()
        cached_hash = LEAN_FILES_HASH_MARKER.read_text().strip()
        if current_version == cached_version and current_hash == cached_hash:
            print(f"Reusing existing test project at {BUILD_DIR}")
            yield BUILD_DIR
            return

    # Clean previous build
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    # Copy lean-toolchain from root
    shutil.copy(lean_toolchain_file, BUILD_DIR / "lean-toolchain")
    lean_version = lean_toolchain_file.read_text().strip()

    # Copy lakefile.toml
    shutil.copy(TEMPLATE_DIR / "lakefile.toml.template", BUILD_DIR / "lakefile.toml")

    # Copy all Lean files, preserving directory structure
    lean_dest = BUILD_DIR / "LeanTestProject"
    if LEAN_FILES.exists():
        shutil.copytree(LEAN_FILES, lean_dest)
    else:
        # Create empty structure if lean_exploit_files doesn't exist yet
        lean_dest.mkdir(parents=True, exist_ok=True)

    # Generate root import file
    imports = []
    for lean_file in lean_dest.rglob("*.lean"):
        rel_path = lean_file.relative_to(BUILD_DIR)
        module = str(rel_path.with_suffix("")).replace("/", ".")
        imports.append(f"import {module}")

    root_file = BUILD_DIR / "LeanTestProject.lean"
    if imports:
        root_file.write_text("\n".join(sorted(imports)))
    else:
        root_file.write_text("-- No test files yet")

    # Save version marker
    version_marker.write_text(lean_version)
    LEAN_FILES_HASH_MARKER.write_text(current_hash)

    try:
        subprocess.run(
            ["lake", "build"],
            cwd=BUILD_DIR,
            check=True,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )
    except subprocess.CalledProcessError as e:
        print(f"Warning: lake build failed: {e.stderr}")
    except subprocess.TimeoutExpired:
        print("Warning: lake build timed out")

    yield BUILD_DIR


@pytest.fixture(scope="session")
def setup_mathlib_benchmark_project():
    """
    Generate Mathlib benchmark project for performance testing.

    Simple setup: just copies lakefile and benchmark file, lets Lake handle the rest.
    """
    lean_toolchain_file = ROOT_DIR / "lean-toolchain"
    template_path = MATHLIB_TEMPLATE_DIR / "MathlibBenchmark.lean.template"

    # Check if we can reuse existing project
    olean_path = (
        MATHLIB_BUILD_DIR
        / ".lake"
        / "build"
        / "lib"
        / "lean"
        / "MathlibBenchmark.olean"
    )
    if olean_path.is_file():
        print(f"Reusing existing Mathlib benchmark project at {MATHLIB_BUILD_DIR}")
        return MATHLIB_BUILD_DIR

    # Ensure project directory exists but keep cached packages to avoid re-cloning
    MATHLIB_BUILD_DIR.mkdir(parents=True, exist_ok=True)

    # Remove previously generated sources to force regeneration while preserving `.lake`
    src_dir = MATHLIB_BUILD_DIR / "MathlibBenchmark"
    if src_dir.exists():
        shutil.rmtree(src_dir)

    root_module_file = MATHLIB_BUILD_DIR / "MathlibBenchmark.lean"
    if root_module_file.exists():
        root_module_file.unlink()

    # Get Lean version to match Mathlib version
    lean_version = lean_toolchain_file.read_text().strip()
    version_tag = lean_version.split(":")[-1] if ":" in lean_version else lean_version

    # Copy essential files and substitute version
    shutil.copy(lean_toolchain_file, MATHLIB_BUILD_DIR / "lean-toolchain")

    lakefile_template = (MATHLIB_TEMPLATE_DIR / "lakefile.toml.template").read_text()
    lakefile_content = lakefile_template.replace("MATHLIB_VERSION", version_tag)
    (MATHLIB_BUILD_DIR / "lakefile.toml").write_text(lakefile_content)

    src_dir = MATHLIB_BUILD_DIR / "MathlibBenchmark"
    src_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(template_path, src_dir / "Benchmark.lean")

    # Provide a root module that re-exports the benchmarks
    root_module_file.write_text("import MathlibBenchmark.Benchmark\n")

    first_time_setup = not (MATHLIB_BUILD_DIR / ".lake").exists()

    if first_time_setup:
        print(f"Building Mathlib benchmark project at {MATHLIB_BUILD_DIR}...")
        print(
            "  This will download Mathlib (~2GB) and may take 10-30 minutes on first run..."
        )
    else:
        print(f"Updating Mathlib benchmark project at {MATHLIB_BUILD_DIR}...")

    # Update dependencies (downloads Mathlib)
    print("  Step 1/3: Downloading Mathlib repository...")
    try:
        subprocess.run(
            ["lake", "update", "--keep-toolchain"],
            cwd=MATHLIB_BUILD_DIR,
            check=True,
            text=True,
            timeout=1800,  # 30 minutes
        )
        if first_time_setup:
            print("  ✓ Mathlib downloaded")
        else:
            print("  ✓ Lake manifest up to date")
    except subprocess.CalledProcessError:
        print("  ✗ lake update failed")
        return MATHLIB_BUILD_DIR
    except subprocess.TimeoutExpired:
        print("  ✗ lake update timed out")
        return MATHLIB_BUILD_DIR

    # Get prebuilt cache
    print("  Step 2/3: Downloading prebuilt Mathlib binaries...")
    try:
        subprocess.run(
            ["lake", "exe", "cache", "get"],
            cwd=MATHLIB_BUILD_DIR,
            check=True,
            text=True,
            timeout=600,
        )
        print("  ✓ Cache downloaded")
    except subprocess.CalledProcessError:
        print("  ⚠ cache get failed, will build from source (slow)")
    except subprocess.TimeoutExpired:
        print("  ⚠ cache get timed out")

    # Build the project
    print("  Step 3/3: Building MathlibBenchmark...")
    try:
        subprocess.run(
            ["lake", "build"],
            cwd=MATHLIB_BUILD_DIR,
            check=True,
            text=True,
            timeout=600,
        )
        print("  ✓ Build complete!")
    except subprocess.CalledProcessError:
        print("  ✗ lake build failed")
    except subprocess.TimeoutExpired:
        print("  ✗ lake build timed out")

    return MATHLIB_BUILD_DIR


@pytest.fixture(scope="session")
def test_project_path(setup_lean_test_project):
    """Return path to built test project"""
    return setup_lean_test_project


@pytest.fixture(scope="session")
def mathlib_verifier(setup_mathlib_benchmark_project):
    """Build LeanParanoia and return verifier interface for Mathlib project"""
    paranoia_path = Path.cwd() / ".lake/build/bin/paranoia"
    build_env = os.environ.get("LEANPARANOIA_BUILD_PARANOIA", "0").strip().lower()
    build_requested = build_env in {"1", "true", "yes", "on"}

    if build_requested or not paranoia_path.exists():
        try:
            subprocess.run(
                ["lake", "exe", "cache", "get"],
                check=True,
                capture_output=True,
                text=True,
                timeout=300,
            )
        except subprocess.CalledProcessError as e:
            print(f"Warning: lake exe cache get failed: {e.stderr}")
        except subprocess.TimeoutExpired:
            print("Warning: lake exe cache get timed out")

        try:
            subprocess.run(["lake", "build"], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Warning: LeanParanoia build failed: {e.stderr.decode()}")

    return Verifier(paranoia_path, setup_mathlib_benchmark_project)


@pytest.fixture(scope="session")
def verifier(setup_lean_test_project):
    """Build LeanParanoia and return verifier interface"""
    paranoia_path = Path.cwd() / ".lake/build/bin/paranoia"
    build_env = os.environ.get("LEANPARANOIA_BUILD_PARANOIA", "0").strip().lower()
    build_requested = build_env in {"1", "true", "yes", "on"}

    if build_requested or not paranoia_path.exists():
        try:
            subprocess.run(["lake", "build"], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Warning: LeanParanoia build failed: {e.stderr.decode()}")

    return Verifier(paranoia_path, setup_lean_test_project)


@pytest.fixture
def default_config():
    """Default verification configuration - all checks enabled"""
    return {
        "checkSorry": True,
        "checkMetavariables": True,
        "checkUnsafe": True,
        "checkAxioms": True,
        "checkConstructors": True,
        "checkRecursors": True,
        "checkExtern": True,
        "checkOpaqueBodies": True,
        "checkSource": True,
        "enableReplay": True,
        "allowedAxioms": ["propext", "Quot.sound", "Classical.choice"],
        "trustModules": [],
    }


@pytest.fixture
def trust_mathlib_config():
    """Configuration that trusts Mathlib and Std, all checks enabled"""
    return {
        "checkSorry": True,
        "checkMetavariables": True,
        "checkUnsafe": True,
        "checkAxioms": True,
        "checkConstructors": True,
        "checkRecursors": True,
        "checkExtern": True,
        "checkOpaqueBodies": True,
        "checkSource": True,
        "enableReplay": False,
        "allowedAxioms": ["propext", "Quot.sound", "Classical.choice"],
        "trustModules": ["Mathlib", "Std"],
    }
