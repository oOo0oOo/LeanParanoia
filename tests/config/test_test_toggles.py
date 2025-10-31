"""Tests for test toggles (enabling/disabling individual tests)."""


import conftest as fixtures


def test_disable_sorry_check(verifier):
    """Test disabling sorry check allows sorry through"""
    config = {"checkSorry": False}
    result = verifier.verify_theorem(
        "LeanTestProject.Sorry.Direct", "exploit_theorem", config=config
    )

    # Should pass if sorry check is disabled
    assert result.success or "NoSorry" not in result.failed_tests


def test_disable_metavariable_check(verifier):
    """Test disabling metavariable check"""
    config = {"checkMetavariables": False}
    result = verifier.verify_theorem(
        "LeanTestProject.Metavariables.FailedSearch", "exploit_theorem", config=config
    )

    assert result.success or "NoMetavars" not in result.failed_tests


def test_disable_unsafe_check(verifier):
    """Test disabling unsafe check"""
    config = {"checkUnsafe": False}
    result = verifier.verify_theorem(
        "LeanTestProject.Unsafe.UnsafeDef", "exploit_theorem", config=config
    )

    assert result.success or "NoUnsafe" not in result.failed_tests


def test_disable_axiom_check(verifier):
    """Test disabling axiom check allows custom axioms"""
    config = {"checkAxioms": False}
    result = verifier.verify_theorem(
        "LeanTestProject.Axioms.False", "exploit_theorem", config=config
    )

    assert result.success or "AxiomWhitelist" not in result.failed_tests


def test_disable_extern_check(verifier):
    """Test disabling extern check"""
    config = {"checkExtern": False}
    result = verifier.verify_theorem(
        "LeanTestProject.Unsafe.Extern", "exploit_theorem", config=config
    )

    assert result.success or "NoExtern" not in result.failed_tests


def test_disable_opaque_body_check(verifier, monkeypatch):
    """Test disabling opaque body inspection propagates to the CLI."""

    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd

        class _Result:
            returncode = 0
            stdout = ""
            stderr = ""

        return _Result()

    monkeypatch.setattr(fixtures.subprocess, "run", fake_run)

    config = {"checkOpaqueBodies": False}
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.Simple", "simple_theorem", config=config
    )

    assert result.success
    assert "--no-opaque-bodies" in captured.get("cmd", [])


def test_enable_replay(verifier):
    """Test enabling replay verification"""
    config = {"enableReplay": True}
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.Simple", "simple_theorem", config=config
    )

    # Should still pass with replay enabled
    assert result.success


def test_disable_all_checks(verifier):
    """Test that disabling all checks allows everything through"""
    config = {
        "checkSorry": False,
        "checkMetavariables": False,
        "checkUnsafe": False,
        "checkAxioms": False,
        "checkConstructors": False,
        "checkRecursors": False,
        "checkExtern": False,
        "checkOpaqueBodies": False,
        "enableReplay": False,
    }
    result = verifier.verify_theorem(
        "LeanTestProject.Sorry.Direct", "exploit_theorem", config=config
    )

    # Should pass with all checks disabled
    assert result.success


def test_fail_fast_returns_first_failure_only(verifier):
    """Fail-fast mode should stop reporting after the first failure."""
    config = {"failFast": True}
    result = verifier.verify_theorem(
        "LeanTestProject.Sorry.Direct", "exploit_theorem", config=config
    )

    assert not result.success
    assert result.failed_tests == ["NoSorry"]
    assert result.errors == ["NoSorry: Theorem 'exploit_theorem' contains sorry"]
