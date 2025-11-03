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
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.temp_dir = project_path / ".safeverify_temp"
        self.temp_dir.mkdir(exist_ok=True)
        self._prepared_files = {}

    def prepare(self, module: str, theorem: str) -> Tuple[Path, Path]:
        """Prepare target and locate submission olean files (not timed)."""
        if (module, theorem) in self._prepared_files:
            return self._prepared_files[(module, theorem)]

        theorem_type, declaration_kind, qualified_theorem_name = self._get_theorem_info(module, theorem)
        target_file = self.temp_dir / f"target_{module.replace('.', '_')}.lean"

        # Create target file with proper namespace structure to match the submission
        # Extract namespace from qualified name
        if '.' in qualified_theorem_name:
            parts = qualified_theorem_name.split('.')
            namespace = '.'.join(parts[:-1])
            simple_name = parts[-1]
            # Axioms can't have proofs
            if declaration_kind == "axiom":
                target_content = f"namespace {namespace}\n\n{declaration_kind} {simple_name} : {theorem_type}\n\nend {namespace}\n"
            else:
                target_content = f"namespace {namespace}\n\n{declaration_kind} {simple_name} : {theorem_type} := sorry\n\nend {namespace}\n"
        else:
            # Axioms can't have proofs
            if declaration_kind == "axiom":
                target_content = f"{declaration_kind} {qualified_theorem_name} : {theorem_type}\n"
            else:
                target_content = f"{declaration_kind} {qualified_theorem_name} : {theorem_type} := sorry\n"

        target_file.write_text(target_content)

        target_olean = self._compile(target_file)
        if not target_olean:
            raise RuntimeError("Failed to compile target")

        submission_olean = self.project_path / ".lake/build/lib/lean" / f"{module.replace('.', '/')}.olean"
        if not submission_olean.exists():
            raise RuntimeError("Submission olean not found")

        self._prepared_files[(module, theorem)] = (target_olean, submission_olean)
        return target_olean, submission_olean

    def run(self, module: str, theorem: str) -> Tuple[str, str]:
        """Run safe_verify (timed portion only)."""
        try:
            target_olean, submission_olean = self._prepared_files[(module, theorem)]
            code, output = run_subprocess(
                ["lake", "exe", "safe_verify", str(target_olean.absolute()), str(submission_olean.absolute())],
                self.project_path
            )

            # Check for test setup issues (false positives)
            test_setup_issues = [
                'not found in submission',
                'does not have the same type',
                'does not match the requirement',
                'is not the same kind as the requirement'
            ]

            output_stripped = output.strip()
            is_test_setup_issue = any(pattern in output_stripped for pattern in test_setup_issues)

            if is_test_setup_issue:
                detected = "n/a"
            else:
                detected = "no" if code == 0 else ("yes" if code > 0 else "n/a")

            return detected, output_stripped
        except Exception as e:
            return "n/a", f"Error: {e}"

    def _get_theorem_info(self, module: str, theorem: str) -> Tuple[str, str, str]:
        """Extract theorem/def type, declaration kind, and qualified name from source file."""
        lean_file = self.project_path / f"{module.replace('.', '/')}.lean"
        if not lean_file.exists():
            return "False", "theorem", theorem
        content = lean_file.read_text()

        # Remove comments to avoid false matches
        # Remove line comments
        content_no_comments = re.sub(r'--[^\n]*', '', content)
        # Remove block comments
        content_no_comments = re.sub(r'/-.*?-/', '', content_no_comments, flags=re.DOTALL)

        # Extract the simple name (last part after the last dot)
        simple_name = theorem.split('.')[-1] if '.' in theorem else theorem

        # Try to find theorem or def with the exact name (with or without namespace)
        for kind in ['theorem', 'def', 'axiom']:
            # Try simple name first (most common case)
            pattern = rf'{kind}\s+{re.escape(simple_name)}\s*(?:\([^)]*\))?\s*:\s*([^:]+?)(?:\s*:=|\s*where|\s*$)'
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            if match:
                theorem_type = match.group(1).strip()
                # Clean up multiline declarations
                theorem_type = ' '.join(theorem_type.split())

                # For target, convert 'axiom' to 'axiom' to match submission exactly
                # (SafeVerify will check the axiom dependencies)
                return_kind = kind

                # Now get the full qualified name for the target
                # Check if there's a namespace declaration (use cleaned content)
                namespace_match = re.search(r'^namespace\s+([A-Za-z0-9_.]+)', content_no_comments, re.MULTILINE)
                if namespace_match:
                    namespace = namespace_match.group(1)
                    qualified_name = f"{namespace}.{simple_name}"
                else:
                    qualified_name = simple_name

                return theorem_type, return_kind, qualified_name

        return "False", "theorem", theorem

    def _compile(self, lean_file: Path):
        """Compile a Lean file to olean."""
        olean = lean_file.with_suffix(".olean")
        if olean.exists():
            olean.unlink()
        code, output = run_subprocess(
            ["lake", "env", "lean", "-o", str(olean.absolute()), str(lean_file.absolute())],
            self.project_path
        )
        if code != 0:
            print(f"Warning: Failed to compile {lean_file.name}: {output[:200]}")
        return olean if olean.exists() else None


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
    setup_tool(project_path, "SafeVerify", "https://github.com/GasStationManager/SafeVerify.git", "main")
    return SafeVerifyRunner(project_path)


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
