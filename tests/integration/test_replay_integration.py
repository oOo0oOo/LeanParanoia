"""
Integration tests for lean4checker replay integration.
"""


def test_replay_with_valid_theorem(verifier):
    """Test replay verification on valid theorem"""
    result = verifier.verify_theorem("LeanTestProject.Valid.Simple", "simple_theorem")

    assert result.success, f"Valid theorem should pass: {result.errors}"
    # Replay is enabled, so EnvironmentReplay should pass
    assert "EnvironmentReplay" not in result.failed_tests


def test_replay_with_helper_dependencies(verifier):
    """Test replay verification with helper dependencies"""
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.Dependencies", "uses_helper"
    )

    assert result.success, f"Valid theorem with deps should pass: {result.errors}"
    assert "EnvironmentReplay" not in result.failed_tests


def test_replay_with_transitive_dependencies(verifier):
    """Test replay verification with multi-level dependencies"""
    result = verifier.verify_theorem(
        "LeanTestProject.Transitive.Level2_UsesBoth", "uses_both"
    )

    assert result.success, f"Valid theorem with deep deps should pass: {result.errors}"
    assert "EnvironmentReplay" not in result.failed_tests


def test_replay_can_be_disabled(verifier):
    """Test that replay can be disabled via config"""
    config = {"enableReplay": False}

    result = verifier.verify_theorem(
        "LeanTestProject.Valid.Simple", "simple_theorem", config=config
    )

    assert result.success


def test_replay_with_whitelisted_axioms(verifier, default_config):
    """Test replay verification with whitelisted axioms"""
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.WithAxioms",
        "uses_choice",
        config=default_config,
    )

    assert result.success, (
        f"Theorem with whitelisted axioms should pass: {result.errors}"
    )
    assert "EnvironmentReplay" not in result.failed_tests


def test_replay_with_sorry_in_dependencies(verifier):
    """Test that replay verification detects sorry in dependencies"""
    result = verifier.verify_theorem(
        "LeanTestProject.Transitive.DeepSorry_L1", "uses_sorry_from_l0"
    )

    assert not result.success
    # Should be caught by NoSorry check (replay doesn't check for sorry)
    assert "NoSorry" in result.failed_tests or len(result.failed_tests) > 0


def test_replay_integration_with_dependencies(verifier):
    """Test that replay verification handles multi-level dependencies correctly"""
    config = {"enableReplay": True}
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.Dependencies", "uses_helper", config=config
    )

    assert result.success
    assert "EnvironmentReplay" not in result.failed_tests


def test_replay_integration_with_deep_dependencies(verifier):
    """Test replay with multi-level transitive dependencies"""
    config = {"enableReplay": True}
    result = verifier.verify_theorem(
        "LeanTestProject.Transitive.Level2_UsesBoth", "uses_both", config=config
    )

    assert result.success
    assert "EnvironmentReplay" not in result.failed_tests


def test_replay_integration_disabled(verifier):
    """Test that disabling replay still allows verification to pass"""
    config = {"enableReplay": False}
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.Simple", "simple_theorem", config=config
    )

    assert result.success


def test_replay_integration_with_axioms(verifier):
    """Test that replay works correctly with whitelisted axioms"""
    config = {
        "enableReplay": True,
        "allowedAxioms": ["propext", "Quot.sound", "Classical.choice"],
    }
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.WithAxioms", "uses_choice", config=config
    )

    assert result.success
    assert "EnvironmentReplay" not in result.failed_tests


def test_replay_integration_catches_sorry(verifier):
    """Test that replay verification works even when sorry is in dependencies"""
    # Even with replay enabled, the NoSorry check should catch this first
    result = verifier.verify_theorem(
        "LeanTestProject.Sorry.Intermediate", "exploit_theorem"
    )

    assert not result.success
    # Should fail on NoSorry check (primary detection)
    assert "NoSorry" in result.failed_tests or len(result.failed_tests) > 0


def test_replay_with_deep_dependencies(verifier):
    """Test replay with multi-level transitive dependencies"""
    config = {"enableReplay": True}
    result = verifier.verify_theorem(
        "LeanTestProject.Transitive.Level2_UsesBoth", "uses_both", config=config
    )

    assert result.success
    assert "Test_EnvironmentReplay" not in result.failed_tests


def test_replay_disabled(verifier):
    """Test that disabling replay still allows verification to pass"""
    config = {"enableReplay": False}
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.Simple", "simple_theorem", config=config
    )

    assert result.success


def test_replay_with_axioms(verifier, default_config):
    """Test that replay works correctly with whitelisted axioms"""
    config = {
        "enableReplay": True,
        "allowedAxioms": ["propext", "Quot.sound", "Classical.choice"],
    }
    result = verifier.verify_theorem(
        "LeanTestProject.Valid.WithAxioms", "uses_choice", config=config
    )

    assert result.success
    assert "Test_EnvironmentReplay" not in result.failed_tests


def test_replay_catches_sorry_in_dependencies(verifier):
    """Test that replay verification works even when sorry is in dependencies"""
    # Even with replay enabled, the NoSorry check should catch this first
    result = verifier.verify_theorem(
        "LeanTestProject.Sorry.Intermediate", "exploit_theorem"
    )

    assert not result.success
    # Should fail on NoSorry check (primary detection)
    assert "Test_NoSorry" in result.failed_tests or len(result.failed_tests) > 0
