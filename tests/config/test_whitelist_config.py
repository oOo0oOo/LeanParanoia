"""
Tests for axiom whitelist configuration.
"""


def test_default_whitelist_allows_standard_axioms(verifier):
    """Test default whitelist allows standard axioms (propext, Quot.sound, Classical.choice)"""
    result = verifier.verify_theorem("LeanTestProject.Valid.WithAxioms", "uses_choice")
    assert result.success


def test_empty_whitelist_rejects_standard_axioms(verifier):
    """Test empty whitelist rejects all axioms including standard ones"""
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.WithAxioms", "uses_choice", allowed_axioms=[]
    )
    assert not result.success
    assert "CustomAxioms" in result.failed_tests


def test_custom_whitelist_allows_specific_axioms(verifier):
    """Test custom whitelist allows only specified axioms"""
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.Simple", "simple_theorem", allowed_axioms=["propext"]
    )
    assert result.success


def test_whitelist_rejects_custom_axioms(verifier):
    """Test that custom axioms are rejected even with standard whitelist"""
    result = verifier.verify_theorem("LeanTestProject.CustomAxioms.ProveFalse", "exploit_theorem")
    assert not result.success
    assert "CustomAxioms" in result.failed_tests
