"""Benchmark: LeanParanoia vs lean4checker vs SafeVerify"""

import json
import re
import subprocess
import timeit
from pathlib import Path
from typing import Dict, List, Tuple

import pytest


TEST_DIR = Path(__file__).parent.parent
ROOT_DIR = TEST_DIR.parent


def collect_test_cases() -> Dict[str, List[Tuple[str, str]]]:
    """Discover exploit files and extract theorem names from test files."""
    explicit_theorems = {}
    for test_file in (TEST_DIR / "exploits").glob("test_*.py"):
        content = test_file.read_text()
        # Match pattern: "LeanTestProject.Module.Name", "theorem_name"
        for match in re.finditer(r'"(LeanTestProject\.[^"]+)",\s*"([^"]+)"', content):
            module = match.group(1)
            theorem = match.group(2)
            explicit_theorems[module] = theorem

    # Helper/library files that are imported by other files but not tested directly
    helper_files = {
        "LeanTestProject.Transitive.BadLib",
        "LeanTestProject.Transitive.DeepAxiom_L0",
        "LeanTestProject.Transitive.DeepSorry_L0",
        "LeanTestProject.Transitive.Level0_Clean",
        "LeanTestProject.Transitive.Level1_UsesClean",
        "LeanTestProject.Valid.Helper",
    }

    categorized = {}
    for lean_file in sorted((TEST_DIR / "lean_exploit_files").rglob("*.lean")):
        parts = lean_file.relative_to(TEST_DIR / "lean_exploit_files").with_suffix("").parts
        if len(parts) >= 2:
            category = parts[0]
            module = "LeanTestProject." + ".".join(parts)

            # Skip helper files that aren't directly tested
            if module in helper_files and module not in explicit_theorems:
                continue

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


def time_function(func, repeat: int = 1) -> float:
    """Time a function call (average of 2 runs) in milliseconds."""
    times = timeit.Timer(func).repeat(repeat=repeat, number=1)
    return (sum(times) / len(times)) * 1000


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

    def prepare(self, module: str, theorem: str) -> Tuple[Path, Path]:
        """Compile reference file and locate submission olean (not timed)."""
        if module in self._compiled_refs:
            return self._compiled_refs[module]

        rel_path = module.replace("LeanTestProject.", "").replace(".", "/") + ".lean"
        ref_file = self.references_dir / rel_path

        if not ref_file.exists():
            raise RuntimeError(f"Reference file not found: {ref_file}")

        # Copy reference to project directory and compile it there
        project_ref_file = self.project_path / rel_path
        project_ref_file.parent.mkdir(parents=True, exist_ok=True)
        project_ref_file.write_text(ref_file.read_text())

        ref_olean = self._compile(project_ref_file)
        if not ref_olean:
            raise RuntimeError(f"Failed to compile reference: {ref_file}")

        submission_olean = self.project_path / ".lake/build/lib/lean" / f"{module.replace('.', '/')}.olean"

        # KernelRejection files don't have oleans (kernel rejected them during compilation)
        if not submission_olean.exists():
            if "KernelRejection" in module:
                # Mark as N/A - these are expected to be rejected by kernel
                self._compiled_refs[module] = None
                return None, None
            raise RuntimeError(f"Submission olean not found: {submission_olean}")

        self._compiled_refs[module] = (ref_olean, submission_olean)
        return ref_olean, submission_olean

    def run(self, module: str, theorem: str) -> Tuple[str, str]:
        """Run safe_verify (timed portion only)."""
        try:
            cached = self._compiled_refs.get(module)
            if cached is None:
                # KernelRejection or other N/A case
                return "n/a", "Kernel rejected during compilation"

            ref_olean, submission_olean = cached
            code, output = run_subprocess(
                ["lake", "exe", "safe_verify", str(ref_olean.absolute()), str(submission_olean.absolute())],
                self.project_path
            )

            # Extract last line as the relevant message
            lines = output.strip().split('\n')
            last_line = lines[-1] if lines else ""

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
            self.project_path
        )

        if code != 0 or not olean.exists():
            raise RuntimeError(f"Failed to compile {lean_file.name}: {output[:200]}")

        return olean


def setup_tool(project_path: Path, tool_name: str, git_url: str, rev: str):
    """Add tool to lakefile and build it."""
    lakefile = project_path / "lakefile.toml"
    content = lakefile.read_text()

    if tool_name not in content:
        content += f'\n[[require]]\nname = "{tool_name}"\ngit = "{git_url}"\nrev = "{rev}"\n'
        lakefile.write_text(content)
        subprocess.run(["lake", "update", "--keep-toolchain", tool_name], cwd=project_path, capture_output=True)
        subprocess.run(["lake", "build", tool_name.lower()], cwd=project_path, capture_output=True, timeout=300)


@pytest.fixture(scope="session")
def lean4checker_runner(test_project_path):
    project_path = Path(test_project_path)
    toolchain = (project_path / "lean-toolchain").read_text().strip()
    lean_version = toolchain.split(":")[-1]
    setup_tool(project_path, "lean4checker", "https://github.com/leanprover/lean4checker.git", lean_version)
    return Lean4CheckerRunner(project_path)


@pytest.fixture(scope="session")
def safeverify_runner(test_project_path):
    project_path = Path(test_project_path)
    references_dir = TEST_DIR / "benchmark" / "references"
    setup_tool(project_path, "SafeVerify", "https://github.com/GasStationManager/SafeVerify.git", "main")
    return SafeVerifyRunner(project_path, references_dir)


@pytest.mark.benchmark_comparison
def test_tool_comparison(verifier, lean4checker_runner, safeverify_runner):
    """Compare LeanParanoia, lean4checker, and SafeVerify on exploit files."""

    results = {}
    for category, cases in collect_test_cases().items():
        category_results = []

        for module, theorem in cases:
            print(f"Testing {module}")

            try:
                lp_time = time_function(lambda: verifier.verify_theorem(module, theorem))
                lp_ff_time = time_function(lambda: verifier.verify_theorem(module, theorem, fail_fast=True))
                result = verifier.verify_theorem(module, theorem)
                lp_detected = "no" if result.success else "yes"
                lp_message = "; ".join(result.failed_tests) if result.failed_tests else ""
            except Exception as e:
                lp_detected, lp_message, lp_time, lp_ff_time = "n/a", str(e), None, None

            try:
                l4c_time = time_function(lambda: lean4checker_runner.run(module))
                l4c_detected, l4c_message = lean4checker_runner.run(module)
            except Exception as e:
                l4c_detected, l4c_message, l4c_time = "n/a", str(e), None

            try:
                safeverify_runner.prepare(module, theorem)
                sv_time = time_function(lambda: safeverify_runner.run(module, theorem))
                sv_detected, sv_message = safeverify_runner.run(module, theorem)
            except Exception as e:
                sv_detected, sv_message, sv_time = "n/a", str(e), None

            category_results.append({
                "exploit_file": module.replace("LeanTestProject.", "").replace(".", "/"),
                "leanparanoia": {
                    "detected": lp_detected,
                    "message": lp_message,
                    "time_ms": round(lp_time) if lp_time else None,
                    "time_failfast_ms": round(lp_ff_time) if lp_ff_time else None,
                },
                "lean4checker": {
                    "detected": l4c_detected,
                    "message": l4c_message,
                    "time_ms": round(l4c_time) if l4c_time else None,
                },
                "safeverify": {
                    "detected": sv_detected,
                    "message": sv_message,
                    "time_ms": round(sv_time) if sv_time else None,
                },
            })

        if category_results:
            results[category] = category_results

    # Write results
    output_file = TEST_DIR / "benchmark" / "comparison_results.json"
    output_file.write_text(json.dumps(results, indent=2))
    assert results


@pytest.mark.benchmark_comparison
def test_completeness():
    """Verify all exploit files are discovered."""
    collected = {m for cases in collect_test_cases().values() for m, _ in cases}
    expected = {
        f"LeanTestProject.{'.'.join(f.relative_to(TEST_DIR / 'lean_exploit_files').with_suffix('').parts)}"
        for f in (TEST_DIR / "lean_exploit_files").rglob("*.lean")
        if len(f.relative_to(TEST_DIR / "lean_exploit_files").parts) >= 2
    }
    assert collected == expected, f"Missing: {expected - collected}"
