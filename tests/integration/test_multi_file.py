"""
Integration tests for multi-file verification.
"""


def test_multi_level_dependencies(verifier):
    """Test verification with multi-level dependencies"""
    result = verifier.verify_theorem(
        "LeanTestProject.Transitive.Level2_UsesBoth", "uses_both"
    )

    assert result.success
