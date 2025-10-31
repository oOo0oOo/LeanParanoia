"""
Tests for trust policies (trusting specific modules to skip verification).
"""


def test_trust_modules_empty_by_default(verifier):
    """Test that no modules are trusted by default"""
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.Simple", "simple_theorem"
    )
    assert result.success


def test_trust_module_skips_verification(verifier):
    """Test that trusted modules skip verification"""
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.Simple",
        "simple_theorem",
        trust_modules=["LeanTestProject.Valid"],
    )
    assert result.success


def test_trust_mathlib_and_std(verifier):
    """Test trusting Mathlib and Std libraries"""
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.Simple",
        "simple_theorem",
        trust_modules=["Mathlib", "Std"],
    )
    assert result.success


def test_trust_does_not_skip_target_module(verifier):
    """Test that trusting a module doesn't skip verification of the target theorem itself"""
    result = verifier.verify_theorem(
        "LeanTestProject.Sorry.Direct",
        "exploit_theorem",
        trust_modules=["LeanTestProject.Sorry"],
    )
    # Should still fail - trust applies to dependencies, not target
    assert not result.success


def test_trust_prefix_matching(verifier):
    """Test that trust policies use prefix matching"""
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.Simple",
        "simple_theorem",
        trust_modules=["LeanTestProject"],
    )
    # Should trust all LeanTestProject.* modules
    assert result.success


def test_multiple_trust_prefixes(verifier):
    """Test multiple trust module prefixes"""
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.Simple",
        "simple_theorem",
        trust_modules=["Mathlib", "Std", "Init"],
    )
    assert result.success
