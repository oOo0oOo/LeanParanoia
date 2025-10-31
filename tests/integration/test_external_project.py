"""
E2E test: Verify user workflow of adding LeanParanoia as a dependency.

Tests the documented installation steps:
  lake add paranoia <repo>
  lake build paranoia
  lake exe paranoia MyTheorem
"""

import subprocess
import shutil
import pytest
from pathlib import Path


@pytest.fixture(scope="module")
def user_project(tmp_path_factory):
    """Setup: Fresh project with LeanParanoia as dependency"""
    project = tmp_path_factory.mktemp("user_project")
    paranoia_root = Path(__file__).parent.parent.parent
    
    # Create minimal project
    (project / "lean-toolchain").write_text(
        (paranoia_root / "lean-toolchain").read_text()
    )
    
    # Manually add paranoia dependency (simulates: lake add paranoia <repo>)
    lakefile = f'''name = "UserProject"
defaultTargets = ["UserProject"]

[[lean_lib]]
name = "UserProject"

[[require]]
name = "paranoia"
path = "{paranoia_root}"
'''
    (project / "lakefile.toml").write_text(lakefile)
    
    (project / "UserProject").mkdir()
    (project / "UserProject" / "Test.lean").write_text(
        'theorem valid : True := trivial\ntheorem invalid : False := by sorry'
    )
    (project / "UserProject.lean").write_text("import UserProject.Test")
    
    # Build the user project first, then paranoia
    subprocess.run(["lake", "build"], cwd=project, check=True, timeout=300)
    subprocess.run(["lake", "build", "paranoia"], cwd=project, check=True, timeout=300)
    
    yield project
    shutil.rmtree(project, ignore_errors=True)


def test_lake_exe_paranoia_works(user_project):
    """Test recommended command: lake exe paranoia"""
    result = subprocess.run(
        ["lake", "exe", "paranoia", "UserProject.Test.valid"],
        cwd=user_project, capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
    assert result.returncode == 0


def test_lake_env_verbose_path_works(user_project):
    """Test verbose command: lake env .lake/packages/paranoia/.lake/build/bin/paranoia"""
    bin_path = user_project / ".lake/packages/paranoia/.lake/build/bin/paranoia"
    if not bin_path.exists():
        print(f"Binary not found at {bin_path}")
        print(f"Contents of .lake/packages: {list((user_project / '.lake/packages').iterdir()) if (user_project / '.lake/packages').exists() else 'does not exist'}")
    assert bin_path.exists()
    
    result = subprocess.run(
        ["lake", "env", str(bin_path), "UserProject.Test.valid"],
        cwd=user_project, capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
    assert result.returncode == 0


def test_detects_exploits(user_project):
    """Verify paranoia actually catches issues"""
    result = subprocess.run(
        ["lake", "exe", "paranoia", "UserProject.Test.invalid"],
        cwd=user_project, capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 1  # Should fail due to sorry
