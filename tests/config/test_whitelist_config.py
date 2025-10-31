"""
Tests for axiom whitelist configuration.
"""



def test_default_whitelist_allows_standard_axioms(verifier, default_config):
    """Test default whitelist allows standard axioms (propext, Quot.sound, Classical.choice)"""
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.WithAxioms", "uses_choice", config=default_config
    )

    assert result.success


def test_strict_config_rejects_all_axioms(verifier, strict_config):
    """Test strict config (empty whitelist) rejects all axioms"""
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.WithAxioms", "uses_choice", config=strict_config
    )

    assert not result.success
    assert "AxiomWhitelist" in result.failed_tests


def test_custom_whitelist_allows_specific_axioms(verifier):
    """Test custom whitelist allows only specified axioms"""
    config = {"allowedAxioms": ["propext"]}
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.Simple", "simple_theorem", config=config
    )

    # Simple theorem should work with minimal whitelist
    assert result.success


def test_whitelist_rejects_custom_axioms(verifier, default_config):
    """Test that custom axioms are rejected even with standard whitelist"""
    result = verifier.verify_theorem(
        "LeanTestProject.Axioms.False", "exploit_theorem", config=default_config
    )

    # Custom axiom should be rejected
    assert not result.success
    assert "AxiomWhitelist" in result.failed_tests


def test_empty_whitelist_rejects_everything(verifier):
    """Test that empty whitelist rejects even standard axioms"""
    config = {"allowedAxioms": []}
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.WithAxioms", "uses_choice", config=config
    )

    assert not result.success
