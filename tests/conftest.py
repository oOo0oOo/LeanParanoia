"""
Pytest configuration and fixtures for LeanParanoia tests.
"""

import os
import json
import pytest
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--leanparanoia-only",
        action="store_true",
        default=False,
        help="Run only LeanParanoia benchmarks, skip other tools for faster testing",
    )


TEST_DIR = Path(__file__).parent
LEAN_FILES = TEST_DIR / "lean_exploit_files"
TEMPLATE_DIR = TEST_DIR / "project_template"
BUILD_DIR = Path(".pytest_cache/LeanTestProject")
MATHLIB_BUILD_DIR = Path(".pytest_cache/MathlibBenchmark")
MATHLIB_TEMPLATE_DIR = TEST_DIR / "mathlib_project"
ROOT_DIR = TEST_DIR.parent


class VerificationResult:
    """Simple result wrapper for backward compatibility"""

    def __init__(self, success: bool, failures: dict):
        self.success = success
        self.failures = failures
        self.failed_tests = list(failures.keys())
        self.errors = [msg for messages in failures.values() for msg in messages]
        self.error_trace = None  # Deprecated


class Verifier:
    """Interface to LeanParanoia verifier"""

    def __init__(self, paranoia_path: Path, test_project_path: Path):
        self.paranoia_path = paranoia_path
        self.test_project_path = test_project_path

    def verify_theorem(
        self,
        module: str,
        theorem: str,
        *,
        check_sorry: bool = True,
        check_metavariables: bool = True,
        check_unsafe: bool = True,
        check_partial: bool = True,
        check_axioms: bool = True,
        check_extern: bool = True,
        check_implemented_by: bool = True,
        check_csimp: bool = True,
        check_native_computation: bool = True,
        check_constructors: bool = True,
        check_recursors: bool = True,
        check_opaque_bodies: bool = True,
        check_source: bool = True,
        enable_replay: bool = True,
        allowed_axioms: Optional[List[str]] = None,
        trust_modules: Optional[List[str]] = None,
        fail_fast: bool = False,
    ) -> VerificationResult:
        """
        Verify a theorem from the test project.

        Args:
            module: e.g., "LeanTestProject.Sorry.Direct"
            theorem: e.g., "exploit_theorem"
            check_*: Enable/disable specific checks (default: all enabled)
            allowed_axioms: Whitelisted axioms (default: propext, Quot.sound, Classical.choice)
            trust_modules: Module prefixes to skip verification
            fail_fast: Stop after first failure

        Returns:
            VerificationResult with success, failures, failed_tests, errors attributes
        """

        theorem_name = f"{module}.{theorem}"
        cmd = ["lake", "env", str(self.paranoia_path), theorem_name]

        # Add flags for disabled checks
        if not check_sorry:
            cmd.append("--no-sorry")
        if not check_metavariables:
            cmd.append("--no-metavariables")
        if not check_unsafe:
            cmd.append("--no-unsafe")
        if not check_partial:
            cmd.append("--no-partial")
        if not check_axioms:
            cmd.append("--no-axioms")
        if not check_extern:
            cmd.append("--no-extern")
        if not check_implemented_by:
            cmd.append("--no-implemented-by")
        if not check_csimp:
            cmd.append("--no-csimp")
        if not check_native_computation:
            cmd.append("--no-native-computation")
        if not check_constructors:
            cmd.append("--no-constructors")
        if not check_recursors:
            cmd.append("--no-recursors")
        if not check_opaque_bodies:
            cmd.append("--no-opaque-bodies")
        if not check_source:
            cmd.append("--no-source-check")
        if not enable_replay:
            cmd.append("--no-replay")

        # Default axioms if not specified
        if allowed_axioms is None:
            allowed_axioms = ["propext", "Quot.sound", "Classical.choice"]
        if allowed_axioms is not None:
            cmd.extend(["--allowed-axioms", ",".join(allowed_axioms)])

        if trust_modules:
            cmd.extend(["--trust-modules", ",".join(trust_modules)])

        if fail_fast:
            cmd.append("--fail-fast")

        try:
            result = subprocess.run(
                cmd,
                cwd=self.test_project_path,
                capture_output=True,
                text=True,
                timeout=300,
            )

            # Parse JSON output
            for output in (result.stdout.strip(), result.stderr.strip()):
                if not output:
                    continue
                try:
                    data = json.loads(output)
                    success = bool(data.get("success", False))
                    failures = {
                        str(k): [str(m) for m in v]
                        for k, v in data.get("failures", {}).items()
                    }
                    return VerificationResult(success, failures)
                except json.JSONDecodeError:
                    continue

            # No JSON found - return based on exit code
            return VerificationResult(result.returncode == 0, {})

        except subprocess.TimeoutExpired:
            return VerificationResult(False, {"Timeout": ["Verification timed out"]})
        except Exception as e:
            return VerificationResult(
                False, {"Error": [f"Error running verifier: {e}"]}
            )


def _build_lean_project(
    build_dir: Path,
    template_dir: Path,
    source_files: Path,
    project_name: str,
    lean_toolchain: Path,
) -> Path:
    """Build a Lean project from template."""
    version_marker = build_dir / ".lean_version"

    # Check if we can reuse existing build
    if build_dir.exists() and version_marker.exists():
        current_version = lean_toolchain.read_text().strip()
        cached_version = version_marker.read_text().strip()
        if current_version == cached_version:
            return build_dir

    # Clean and recreate
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True, exist_ok=True)

    # Copy essential files
    shutil.copy(lean_toolchain, build_dir / "lean-toolchain")
    shutil.copy(template_dir / "lakefile.toml.template", build_dir / "lakefile.toml")

    # Copy source files
    dest = build_dir / project_name
    if source_files.exists():
        shutil.copytree(source_files, dest)
    else:
        dest.mkdir(parents=True, exist_ok=True)

    # Generate root import file
    imports = [
        f"import {str(f.relative_to(build_dir).with_suffix('')).replace('/', '.')}"
        for f in dest.rglob("*.lean")
    ]
    root_file = build_dir / f"{project_name}.lean"
    root_file.write_text("\n".join(sorted(imports)) if imports else "-- No files")

    # Save version
    version_marker.write_text(lean_toolchain.read_text().strip())

    # Build
    try:
        subprocess.run(
            ["lake", "build"],
            cwd=build_dir,
            check=True,
            capture_output=True,
            timeout=300,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"Warning: lake build had issues: {e}")

    return build_dir


@pytest.fixture(scope="session", autouse=True)
def setup_lean_test_project():
    """Generate Lean test project dynamically before running tests."""
    yield _build_lean_project(
        BUILD_DIR,
        TEMPLATE_DIR,
        LEAN_FILES,
        "LeanTestProject",
        ROOT_DIR / "lean-toolchain",
    )


@pytest.fixture(scope="session")
def setup_mathlib_benchmark_project():
    """Generate Mathlib benchmark project for performance testing."""
    lean_toolchain = ROOT_DIR / "lean-toolchain"
    olean_path = (
        MATHLIB_BUILD_DIR
        / ".lake"
        / "build"
        / "lib"
        / "lean"
        / "MathlibBenchmark.olean"
    )

    # Reuse if already built
    if olean_path.is_file():
        return MATHLIB_BUILD_DIR

    MATHLIB_BUILD_DIR.mkdir(parents=True, exist_ok=True)

    # Clean source files but keep .lake cache
    for path in [
        MATHLIB_BUILD_DIR / "MathlibBenchmark",
        MATHLIB_BUILD_DIR / "MathlibBenchmark.lean",
    ]:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

    # Setup project
    lean_version = lean_toolchain.read_text().strip()
    version_tag = lean_version.split(":")[-1] if ":" in lean_version else lean_version

    shutil.copy(lean_toolchain, MATHLIB_BUILD_DIR / "lean-toolchain")

    lakefile_template = (MATHLIB_TEMPLATE_DIR / "lakefile.toml.template").read_text()
    (MATHLIB_BUILD_DIR / "lakefile.toml").write_text(
        lakefile_template.replace("MATHLIB_VERSION", version_tag)
    )

    src_dir = MATHLIB_BUILD_DIR / "MathlibBenchmark"
    src_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(
        MATHLIB_TEMPLATE_DIR / "MathlibBenchmark.lean.template",
        src_dir / "Benchmark.lean",
    )
    (MATHLIB_BUILD_DIR / "MathlibBenchmark.lean").write_text(
        "import MathlibBenchmark.Benchmark\n"
    )

    # Build with cache
    for cmd in [
        ["lake", "update", "--keep-toolchain"],
        ["lake", "exe", "cache", "get"],
        ["lake", "build"],
    ]:
        try:
            subprocess.run(cmd, cwd=MATHLIB_BUILD_DIR, check=True, timeout=600)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass  # Continue anyway

    return MATHLIB_BUILD_DIR


@pytest.fixture(scope="session")
def test_project_path(setup_lean_test_project):
    """Return path to built test project"""
    return setup_lean_test_project


def _build_paranoia() -> Path:
    """Build LeanParanoia if needed."""
    paranoia_path = Path.cwd() / ".lake/build/bin/paranoia"
    build_env = os.environ.get("LEANPARANOIA_BUILD_PARANOIA", "0").strip().lower()

    if build_env in {"1", "true", "yes", "on"} or not paranoia_path.exists():
        try:
            subprocess.run(["lake", "build"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            pass  # Continue with potentially stale binary

    return paranoia_path


@pytest.fixture(scope="session")
def verifier(setup_lean_test_project):
    """Build LeanParanoia and return verifier interface for test project"""
    return Verifier(_build_paranoia(), setup_lean_test_project)


@pytest.fixture(scope="session")
def mathlib_verifier(setup_mathlib_benchmark_project):
    """Build LeanParanoia and return verifier interface for Mathlib project"""
    return Verifier(_build_paranoia(), setup_mathlib_benchmark_project)
