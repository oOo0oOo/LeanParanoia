"""
Integration tests for full verification pipeline.
"""


def test_verify_valid_theorem(verifier):
    """Test verification of valid theorem"""
    result = verifier.verify_theorem("LeanTestProject.Valid.Simple", "simple_theorem")
    assert result.success


def test_verify_with_dependencies(verifier):
    """Test verification of theorem with dependencies"""
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.Dependencies", "uses_helper"
    )
    assert result.success


def test_verify_with_whitelisted_axioms(verifier):
    """Test verification with whitelisted axioms"""
    result = verifier.verify_theorem("LeanTestProject.Valid.WithAxioms", "uses_choice")
    assert result.success
