"""Tests for command-line argument parsing."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest


SIMPLE_THEOREM = "LeanTestProject.Valid.Simple.simple_theorem"
CHOICE_THEOREM = "LeanTestProject.Valid.WithAxioms.uses_choice"


def _run_cli(
    paranoia_exe: Path | str, project_path: Path, *args: str, timeout: int = 90
) -> subprocess.CompletedProcess[str]:
    """Execute paranoia via lake env inside the generated test project."""
    exe = Path(paranoia_exe).resolve()
    cmd = ["lake", "env", str(exe), *args]
    return subprocess.run(
        cmd,
        cwd=project_path,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _combined_output(result: subprocess.CompletedProcess[str]) -> str:
    return (result.stdout or "") + (result.stderr or "")


@pytest.fixture
def paranoia_exe() -> Path:
    """Ensure the paranoia binary is built before running CLI tests."""
    subprocess.run(["lake", "build"], check=True, capture_output=True)
    return Path.cwd() / ".lake/build/bin/paranoia"


def test_allowed_axioms_parsing(paranoia_exe: Path, test_project_path: Path):
    """Test that --allowed-axioms accepts comma-separated values."""
    result = _run_cli(
        paranoia_exe,
        test_project_path,
        "--allowed-axioms",
        "propext,Quot.sound",
        SIMPLE_THEOREM,
    )

    assert result.returncode == 0
    assert "Unknown option" not in result.stderr
    assert "requires a comma-separated list" not in result.stderr


def test_allowed_axioms_single_value(paranoia_exe: Path, test_project_path: Path):
    """Test --allowed-axioms with a single axiom value."""
    result = _run_cli(
        paranoia_exe, test_project_path, "--allowed-axioms", "propext", SIMPLE_THEOREM
    )

    assert result.returncode == 0
    assert "CustomAxioms" not in _combined_output(result)


def test_allowed_axioms_empty_list(paranoia_exe: Path, test_project_path: Path):
    """Test that empty --allowed-axioms rejects axioms requiring choice."""
    result = _run_cli(
        paranoia_exe, test_project_path, "--allowed-axioms", "", CHOICE_THEOREM
    )

    output = _combined_output(result)
    assert result.returncode != 0
    assert "CustomAxioms" in output
    assert "Classical.choice" in output


def test_allowed_axioms_missing_value_error(
    paranoia_exe: Path, test_project_path: Path
):
    """Test that omitting the --allowed-axioms value is rejected."""
    result = _run_cli(paranoia_exe, test_project_path, "--allowed-axioms")

    assert result.returncode != 0
    assert "requires a comma-separated list" in _combined_output(result).lower()


def test_trust_modules_parsing(paranoia_exe: Path, test_project_path: Path):
    """Test that --trust-modules accepts comma-separated prefixes."""
    result = _run_cli(
        paranoia_exe,
        test_project_path,
        "--trust-modules",
        "LeanTestProject.Valid,Mathlib",
        SIMPLE_THEOREM,
    )

    assert result.returncode == 0
    assert "Unknown option" not in result.stderr
    assert "requires a comma-separated list" not in result.stderr


def test_trust_modules_single_value(paranoia_exe: Path, test_project_path: Path):
    """Test --trust-modules with a single prefix."""
    result = _run_cli(
        paranoia_exe,
        test_project_path,
        "--trust-modules",
        "LeanTestProject.Valid",
        SIMPLE_THEOREM,
    )

    assert result.returncode == 0


def test_trust_modules_empty_list(paranoia_exe: Path, test_project_path: Path):
    """Test that empty --trust-modules behaves like the default."""
    result = _run_cli(
        paranoia_exe, test_project_path, "--trust-modules", "", SIMPLE_THEOREM
    )

    assert result.returncode == 0


def test_trust_modules_missing_value_error(paranoia_exe: Path, test_project_path: Path):
    """Test that omitting the --trust-modules value is rejected."""
    result = _run_cli(paranoia_exe, test_project_path, "--trust-modules")

    assert result.returncode != 0
    assert "requires a comma-separated list" in _combined_output(result).lower()


def test_fail_fast_flag(paranoia_exe: Path, test_project_path: Path):
    """Test that --fail-fast is accepted."""
    result = _run_cli(paranoia_exe, test_project_path, "--fail-fast", SIMPLE_THEOREM)

    assert result.returncode == 0
    assert "Unknown option" not in result.stderr


def test_fail_fast_limits_failures(paranoia_exe: Path, test_project_path: Path):
    """Test that --fail-fast stops after the first failing check."""
    failing_theorem = "LeanTestProject.Sorry.Direct.exploit_theorem"
    result = _run_cli(paranoia_exe, test_project_path, "--fail-fast", failing_theorem)

    assert result.returncode != 0
    payload = json.loads(_combined_output(result))
    assert payload["failures"] == {
        "Sorry": ["Theorem 'LeanTestProject.Sorry.Direct.exploit_theorem' contains sorry"]
    }


def test_combined_axioms_and_trust_modules(paranoia_exe: Path, test_project_path: Path):
    """Test using both --allowed-axioms and --trust-modules together."""
    result = _run_cli(
        paranoia_exe,
        test_project_path,
        "--allowed-axioms",
        "propext,Quot.sound,Classical.choice",
        "--trust-modules",
        "LeanTestProject.Valid,Std",
        CHOICE_THEOREM,
    )

    assert result.returncode == 0
    assert "Unknown option" not in result.stderr


def test_help_shows_new_options(paranoia_exe: Path, test_project_path: Path):
    """Test that --help documents the new command line options."""
    result = _run_cli(paranoia_exe, test_project_path, "--help")

    output = _combined_output(result)
    assert result.returncode == 0
    assert "--allowed-axioms" in output
    assert "--trust-modules" in output
    assert "--fail-fast" in output
    assert "comma" in output.lower()


def test_options_preserve_other_flags(paranoia_exe: Path, test_project_path: Path):
    """Test that new options work alongside existing CLI flags."""
    result = _run_cli(
        paranoia_exe,
        test_project_path,
        "--no-sorry",
        "--allowed-axioms",
        "propext",
        "--no-metavariables",
        SIMPLE_THEOREM,
    )

    assert result.returncode == 0
    assert "Unknown option" not in result.stderr


def test_default_axioms_preserved_without_flag(
    paranoia_exe: Path, test_project_path: Path
):
    """Test default whitelist still allows axioms used by valid theorem."""
    result = _run_cli(paranoia_exe, test_project_path, CHOICE_THEOREM)

    assert result.returncode == 0


def test_default_trust_modules_empty_without_flag(
    paranoia_exe: Path, test_project_path: Path
):
    """Test default trust-modules setting keeps verification active."""
    result = _run_cli(paranoia_exe, test_project_path, SIMPLE_THEOREM)

    assert result.returncode == 0
