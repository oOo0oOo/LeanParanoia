"""Benchmark: LeanParanoia vs lean4checker vs SafeVerify vs Comparator"""

import json
import platform
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import pytest


TEST_DIR = Path(__file__).parent.parent
ROOT_DIR = TEST_DIR.parent

HELPER_FILES = {
    "LeanTestProject.Transitive.BadLib",
    "LeanTestProject.Transitive.DeepAxiom_L0",
    "LeanTestProject.Transitive.DeepSorry_L0",
    "LeanTestProject.Transitive.Level0_Clean",
    "LeanTestProject.Transitive.Level1_UsesClean",
}


def collect_test_cases() -> Dict[str, List[Tuple[str, str]]]:
    """Discover exploit files and extract theorem names from test files."""
    explicit_theorems = {}
    for test_file in (TEST_DIR / "exploits").glob("test_*.py"):
        content = test_file.read_text()
        for match in re.finditer(r'"(LeanTestProject\.[^"]+)",\s*"([^"]+)"', content):
            explicit_theorems[match.group(1)] = match.group(2)

    categorized = {}
    for lean_file in sorted((TEST_DIR / "lean_exploit_files").rglob("*.lean")):
        parts = lean_file.relative_to(TEST_DIR / "lean_exploit_files").with_suffix("").parts
        if len(parts) >= 2: 
            module = "LeanTestProject." + ".".join(parts)
            if module in HELPER_FILES and module not in explicit_theorems:
                continue

            category = parts[0]
            theorem = explicit_theorems.get(module, "exploit_theorem")
            categorized.setdefault(category, []).append((module, theorem))

    return categorized


def run_subprocess(cmd: List[str], cwd: Path, timeout: int = 60) -> Tuple[int, str]:
    """Run subprocess and return (exit_code, output)."""
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return -1, "Timeout"
    except Exception as e:
        return -2, f"Error: {e}"


def time_and_run(func: Callable[[], Any]) -> Tuple[float, Any]:
    """Run a function and return (time_ms, result)."""
    start = time.perf_counter()
    result = func()
    return (time.perf_counter() - start) * 1000, result


class Lean4CheckerRunner:
    def __init__(self, project_path: Path):
        self.project_path = project_path

    def run(self, module: str) -> Tuple[str, str]:
        code, output = run_subprocess(["lake", "exe", "lean4checker", module], self.project_path)
        detected = "no" if code == 0 else ("yes" if code > 0 else "n/a")
        return detected, output.strip()


class SafeVerifyRunner:
    def __init__(self, project_path: Path, references_dir: Path):
        self.project_path = project_path
        self.references_dir = references_dir
        self._compiled_refs = {}

    def prepare(self, module: str, theorem: str) -> Optional[Tuple[Path, Path]]:
        """Compile reference file and locate submission olean (not timed)."""
        if module in self._compiled_refs:
            return self._compiled_refs[module]

        rel_path = module.replace("LeanTestProject.", "").replace(".", "/") + ".lean"
        ref_file = self.references_dir / rel_path

        if not ref_file.exists():
            raise RuntimeError(f"Reference file not found: {ref_file}")

        project_ref_file = self.project_path / rel_path
        project_ref_file.parent.mkdir(parents=True, exist_ok=True)
        project_ref_file.write_text(ref_file.read_text())

        ref_olean = self._compile(project_ref_file)
        if not ref_olean:
            raise RuntimeError(f"Failed to compile reference: {ref_file}")

        submission_olean = (
            self.project_path / ".lake/build/lib/lean" / f"{module.replace('.', '/')}.olean"
        )

        if not submission_olean.exists():
            if "KernelRejection" in module:
                self._compiled_refs[module] = None
                return None
            raise RuntimeError(f"Submission olean not found: {submission_olean}")

        self._compiled_refs[module] = (ref_olean, submission_olean)
        return ref_olean, submission_olean

    def run(self, module: str, theorem: str) -> Tuple[str, str]:
        """Run safe_verify (timed portion only)."""
        try:
            cached = self._compiled_refs.get(module)
            if cached is None:
                return "n/a", "Kernel rejected during compilation"

            ref_olean, submission_olean = cached
            code, output = run_subprocess(
                ["lake", "exe", "safe_verify", str(ref_olean.absolute()), str(submission_olean.absolute())],
                self.project_path,
            )

            last_line = output.strip().split("\n")[-1] if output.strip() else ""
            detected = "no" if code == 0 else "yes"
            return detected, last_line
        except Exception as e:
            return "n/a", f"Error: {e}"

    def _compile(self, lean_file: Path) -> Path:
        """Compile a Lean file to olean."""
        olean = lean_file.with_suffix(".olean")
        if olean.exists():
            olean.unlink()

        code, output = run_subprocess(
            ["lake", "env", "lean", "-o", str(olean.absolute()), str(lean_file.absolute())],
            self.project_path,
        )

        if code != 0 or not olean.exists():
            raise RuntimeError(f"Failed to compile {lean_file.name}: {output[:200]}")
        return olean


class ComparatorRunner:
    """Comparator tool runner (requires Linux + landrun + lean4export + comparator)."""

    def __init__(self, project_path: Path, references_dir: Path):
        self.project_path = project_path
        self.references_dir = references_dir
        self.config_dir = project_path / ".comparator_configs"
        self.config_dir.mkdir(exist_ok=True)
        self._available = None

    def is_available(self) -> bool:
        """Check if comparator can run (cached)."""
        if self._available is None:
            self._available = platform.system() == "Linux" and all(
                shutil.which(cmd) for cmd in ["landrun", "lean4export", "comparator"]
            )
        return self._available

    def prepare(self, module: str, theorem: str) -> Optional[Path]:
        """Generate config JSON using separate Reference module for solution."""
        parts = module.split('.')
        if len(parts) < 3 or parts[0] != "LeanTestProject":
            return None

        category, test_name = parts[1], parts[2]
        ref_file = self.references_dir / category / f"{test_name}.lean"
        if not ref_file.exists():
            return None

        # Create reference module with renamed namespace
        ref_dir = self.project_path / "Reference" / category
        ref_dir.mkdir(parents=True, exist_ok=True)

        ref_content = ref_file.read_text()
        old_ns = f"LeanTestProject.{category}.{test_name}"
        new_ns = f"Reference.{category}.{test_name}"
        ref_content = ref_content.replace(f"namespace {old_ns}", f"namespace {new_ns}")
        ref_content = ref_content.replace(f"end {old_ns}", f"end {new_ns}")
        (ref_dir / f"{test_name}.lean").write_text(ref_content)

        # Update lakefile to include Reference root
        self._update_lakefile()

        # Update project imports
        self._add_import(f"Reference.{category}.{test_name}")

        # Generate config and build
        config = {
            "challenge_module": module,
            "solution_module": new_ns,
            "theorem_names": [theorem],
            "permitted_axioms": [],
        }
        config_path = self.config_dir / f"{module.replace('.', '_')}.json"
        config_path.write_text(json.dumps(config, indent=2))

        run_subprocess(["lake", "build", new_ns], self.project_path, timeout=120)
        return config_path

    def _update_lakefile(self):
        """Add Reference to lakefile roots if not present."""
        lakefile = self.project_path / "lakefile.toml"
        if lakefile.exists():
            content = lakefile.read_text()
            if 'roots = ["LeanTestProject"]' in content and "Reference" not in content:
                content = content.replace(
                    'roots = ["LeanTestProject"]',
                    'roots = ["LeanTestProject", "Reference"]'
                )
                lakefile.write_text(content)

    def _add_import(self, import_line: str):
        """Add import to project file if not present."""
        project_file = self.project_path / "LeanTestProject.lean"
        if project_file.exists():
            content = project_file.read_text()
            full_import = f"import {import_line}"
            if full_import not in content:
                lines = content.split('\n')
                import_idx = max(
                    (i + 1 for i, line in enumerate(lines) if line.startswith('import ')),
                    default=0
                )
                lines.insert(import_idx, full_import)
                project_file.write_text('\n'.join(lines))

    def run(self, module: str, theorem: str) -> Tuple[str, str]:
        """Run comparator (timed portion only)."""
        if not self.is_available():
            missing = [platform.system() != "Linux" and "Linux"] + [
                cmd for cmd in ["landrun", "lean4export", "comparator"] if not shutil.which(cmd)
            ]
            return "n/a", f"Missing: {', '.join(filter(None, missing))}"

        try:
            config_path = self.prepare(module, theorem)
            if not config_path:
                return "n/a", "Config generation failed"

            code, output = run_subprocess(
                ["lake", "env", "comparator", str(config_path.absolute())],
                self.project_path,
                timeout=120,
            )

            if "PANIC" in output:
                return "n/a", "PANIC " + output.strip()

            detected = "no" if code == 0 else ("yes" if code > 0 else "n/a")
            last_line = output.strip().split("\n")[-1] if output.strip() else ""
            return detected, last_line
        except Exception as e:
            return "n/a", f"Error: {e}"


def setup_tool(project_path: Path, tool_name: str, git_url: str = "", rev: str = "", tool_path: Path = None):
    """Add tool to lakefile and build it."""
    lakefile = project_path / "lakefile.toml"
    content = lakefile.read_text()

    if tool_name in content:
        return

    if tool_path:
        content += f'\n[[require]]\nname = "{tool_name}"\npath = "{tool_path.absolute()}"\n'
    else:
        content += f'\n[[require]]\nname = "{tool_name}"\ngit = "{git_url}"\nrev = "{rev}"\n'

    lakefile.write_text(content)

    for cmd in [
        ["lake", "update", "--keep-toolchain", tool_name],
        ["lake", "clean", tool_name.lower()],
        ["lake", "build", tool_name.lower()],
    ]:
        subprocess.run(cmd, cwd=project_path, capture_output=True, timeout=300)


@pytest.fixture(scope="session")
def lean4checker_runner(test_project_path):
    project_path = Path(test_project_path)
    lean_version = (project_path / "lean-toolchain").read_text().strip().split(":")[-1]
    setup_tool(project_path, "lean4checker", "https://github.com/leanprover/lean4checker.git", lean_version)
    return Lean4CheckerRunner(project_path)


@pytest.fixture(scope="session")
def safeverify_runner(test_project_path):
    project_path = Path(test_project_path)
    references_dir = TEST_DIR / "benchmark" / "references"
    setup_tool(project_path, "SafeVerify", "https://github.com/GasStationManager/SafeVerify.git", "main")

    runner = SafeVerifyRunner(project_path, references_dir)
    print("Warming up SafeVerify...")
    run_subprocess(["lake", "build", "safe_verify"], project_path)
    return runner


@pytest.fixture(scope="session")
def comparator_runner(test_project_path):
    """Setup comparator if available (optional - Linux only)."""
    project_path = Path(test_project_path)
    references_dir = TEST_DIR / "benchmark" / "references"
    runner = ComparatorRunner(project_path, references_dir)

    if not runner.is_available():
        print("⚠️  Comparator skipped (requires Linux + landrun + lean4export + comparator)")
        print("   See tests/benchmark/COMPARATOR_SETUP.md for installation")

    return runner


@pytest.mark.benchmark_comparison
def test_tool_comparison(verifier, lean4checker_runner, safeverify_runner, comparator_runner, request):
    """Compare LeanParanoia, lean4checker, SafeVerify, and Comparator on exploit files.

    Use --leanparanoia-only to skip other tools for faster benchmarking.
    Use --exploit-filter to test specific exploits (e.g., 'AuxiliaryShadowing').
    """
    leanparanoia_only = request.config.getoption("--leanparanoia-only", default=False)
    exploit_filter = request.config.getoption("--exploit-filter", default=None)

    skip_tools = {
        "leanparanoia": request.config.getoption("--skip-leanparanoia", default=False),
        "lean4checker": request.config.getoption("--skip-lean4checker", default=False) or leanparanoia_only,
        "safeverify": request.config.getoption("--skip-safeverify", default=False) or leanparanoia_only,
        "comparator": request.config.getoption("--skip-comparator", default=False) 
                      or leanparanoia_only 
                      or not comparator_runner.is_available(),
    }

    def run_tool(tool_name: str, runner, module: str, theorem: str = None):
        """Run a tool and return (detected, message, time_ms, extra_time_ms)."""
        if skip_tools[tool_name]:
            return "n/a", "skipped", None, None

        try:
            if tool_name == "leanparanoia":
                lp_time, result = time_and_run(lambda: verifier.verify_theorem(module, theorem))
                lp_ff_time, _ = time_and_run(lambda: verifier.verify_theorem(module, theorem, fail_fast=True))
                detected = "no" if result.success else "yes"
                message = "; ".join(result.failed_tests) if result.failed_tests else ""
                return detected, message, lp_time, lp_ff_time

            if tool_name == "lean4checker":
                timing, (detected, message) = time_and_run(lambda: runner.run(module))
                return detected, message, timing, None

            if tool_name in ["safeverify", "comparator"]:
                runner.prepare(module, theorem)
                timing, (detected, message) = time_and_run(lambda: runner.run(module, theorem))
                return detected, message, timing, None

            return "n/a", f"Unknown tool: {tool_name}", None, None
        except Exception as e:
            return "n/a", str(e), None, None

    results = {}
    test_cases = collect_test_cases()
    print(f"Collected categories: {test_cases.keys()}")

    for category, cases in test_cases.items():
        category_results = []

        for module, theorem in cases:
            if exploit_filter and exploit_filter not in module:
                continue

            print(f"Testing {module}")

            lp_det, lp_msg, lp_time, lp_ff_time = run_tool("leanparanoia", verifier, module, theorem)
            l4c_det, l4c_msg, l4c_time, _ = run_tool("lean4checker", lean4checker_runner, module)
            sv_det, sv_msg, sv_time, _ = run_tool("safeverify", safeverify_runner, module, theorem)
            cmp_det, cmp_msg, cmp_time, _ = run_tool("comparator", comparator_runner, module, theorem)

            category_results.append({
                "exploit_file": module.replace("LeanTestProject.", "").replace(".", "/"),
                "leanparanoia": {
                    "detected": lp_det,
                    "message": lp_msg,
                    "time_ms": round(lp_time) if lp_time else None,
                    "time_failfast_ms": round(lp_ff_time) if lp_ff_time else None,
                },
                "lean4checker": {
                    "detected": l4c_det,
                    "message": l4c_msg,
                    "time_ms": round(l4c_time) if l4c_time else None,
                },
                "safeverify": {
                    "detected": sv_det,
                    "message": sv_msg,
                    "time_ms": round(sv_time) if sv_time else None,
                },
                "comparator": {
                    "detected": cmp_det,
                    "message": cmp_msg,
                    "time_ms": round(cmp_time) if cmp_time else None,
                },
            })

        if category_results:
            results[category] = category_results

    # Merge results with existing data
    output_file = TEST_DIR / "benchmark" / "comparison_results.json"
    if output_file.exists():
        existing = json.loads(output_file.read_text())
        for category, category_results in results.items():
            if category in existing:
                existing_map = {r["exploit_file"]: r for r in existing[category]}
                existing_map.update({r["exploit_file"]: r for r in category_results})
                existing[category] = list(existing_map.values())
            else:
                existing[category] = category_results
        results = existing

    output_file.write_text(json.dumps(results, indent=2))
    assert results


@pytest.mark.benchmark_comparison
def test_completeness():
    """Verify all exploit files are discovered (excluding helper files)."""
    collected = {m for cases in collect_test_cases().values() for m, _ in cases}

    all_files = {
        f"LeanTestProject.{'.'.join(f.relative_to(TEST_DIR / 'lean_exploit_files').with_suffix('').parts)}"
        for f in (TEST_DIR / "lean_exploit_files").rglob("*.lean")
        if len(f.relative_to(TEST_DIR / "lean_exploit_files").parts) >= 2
    }

    expected = all_files - HELPER_FILES
    assert collected == expected, f"Missing: {expected - collected}, Extra: {collected - expected}"
