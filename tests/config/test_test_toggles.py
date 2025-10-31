"""Tests for test toggles (enabling/disabling individual tests)."""


def test_disable_sorry_check(verifier):
    """Test disabling sorry check allows sorry through"""
    result = verifier.verify_theorem(
        "LeanTestProject.Sorry.Direct", "exploit_theorem", check_sorry=False
    )
    assert result.success or "NoSorry" not in result.failed_tests


def test_disable_metavariable_check(verifier):
    """Test disabling metavariable check"""
    result = verifier.verify_theorem(
        "LeanTestProject.Metavariables.FailedSearch",
        "exploit_theorem",
        check_metavariables=False,
    )
    assert result.success or "NoMetavars" not in result.failed_tests


def test_disable_unsafe_check(verifier):
    """Test disabling unsafe check"""
    result = verifier.verify_theorem(
        "LeanTestProject.Unsafe.UnsafeDef", "exploit_theorem", check_unsafe=False
    )
    assert result.success or "NoUnsafe" not in result.failed_tests


def test_disable_axiom_check(verifier):
    """Test disabling axiom check allows custom axioms"""
    result = verifier.verify_theorem(
        "LeanTestProject.Axioms.False", "exploit_theorem", check_axioms=False
    )
    assert result.success or "AxiomWhitelist" not in result.failed_tests


def test_disable_extern_check(verifier):
    """Test disabling extern check"""
    result = verifier.verify_theorem(
        "LeanTestProject.Unsafe.Extern", "exploit_theorem", check_extern=False
    )
    assert result.success or "NoExtern" not in result.failed_tests


def test_disable_opaque_body_check(verifier):
    """Test disabling opaque body inspection"""
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.Simple", "simple_theorem", check_opaque_bodies=False
    )
    assert result.success


def test_enable_replay(verifier):
    """Test enabling replay verification"""
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.Simple", "simple_theorem", enable_replay=True
    )
    assert result.success


def test_disable_all_checks(verifier):
    """Test that disabling all checks allows everything through"""
    result = verifier.verify_theorem(
        "LeanTestProject.Sorry.Direct",
        "exploit_theorem",
        check_sorry=False,
        check_metavariables=False,
        check_unsafe=False,
        check_axioms=False,
        check_constructors=False,
        check_recursors=False,
        check_extern=False,
        check_opaque_bodies=False,
        enable_replay=False,
    )
    assert result.success


def test_fail_fast_returns_first_failure_only(verifier):
    """Fail-fast mode should stop reporting after the first failure."""
    result = verifier.verify_theorem(
        "LeanTestProject.Sorry.Direct", "exploit_theorem", fail_fast=True
    )
    assert not result.success
    assert result.failed_tests == ["NoSorry"]
    assert result.errors == ["Theorem 'exploit_theorem' contains sorry"]
