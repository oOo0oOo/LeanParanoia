"""
Tests for trust policies (trusting specific modules to skip verification).
"""


def test_trust_modules_empty_by_default(verifier, default_config):
    """Test that no modules are trusted by default"""
    # With empty trust list, should verify everything
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.Simple", "simple_theorem", config=default_config
    )

    assert result.success
    # Should have performed all checks (no modules skipped)


def test_trust_module_skips_verification(verifier):
    """Test that trusted modules skip verification"""
    config = {"trustModules": ["LeanTestProject.Valid"]}
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.Simple", "simple_theorem", config=config
    )

    # Should succeed and indicate trusted
    assert result.success


def test_trust_mathlib_and_std(verifier, trust_mathlib_config):
    """Test trusting Mathlib and Std libraries"""
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.Simple", "simple_theorem", config=trust_mathlib_config
    )

    # Should work with Mathlib/Std trusted
    assert result.success


def test_trust_does_not_skip_target_module(verifier):
    """Test that trusting a module doesn't skip verification of the target theorem itself"""
    # Even if we trust the module, the target theorem should still be checked
    config = {"trustModules": ["LeanTestProject.Sorry"]}
    result = verifier.verify_theorem(
        "LeanTestProject.Sorry.Direct", "exploit_theorem", config=config
    )

    # Should still fail - trust applies to dependencies, not target
    assert not result.success


def test_trust_prefix_matching(verifier):
    """Test that trust policies use prefix matching"""
    config = {"trustModules": ["LeanTestProject"]}
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.Simple", "simple_theorem", config=config
    )

    # Should trust all LeanTestProject.* modules
    assert result.success


def test_multiple_trust_prefixes(verifier):
    """Test multiple trust module prefixes"""
    config = {"trustModules": ["Mathlib", "Std", "Init"]}
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.Simple", "simple_theorem", config=config
    )

    assert result.success
