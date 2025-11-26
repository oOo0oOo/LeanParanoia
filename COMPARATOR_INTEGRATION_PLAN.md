# Comparator Integration Plan

## Overview

This document outlines a plan to add [leanprover/comparator](https://github.com/leanprover/comparator) to the tool comparison benchmarks in LeanParanoia.

## Version Compatibility Analysis

### Current Versions

| Component | LeanParanoia | Comparator | lean4export |
|-----------|--------------|------------|-------------|
| Lean toolchain | `v4.25.0` | `v4.25.0-rc2` | `v4.25.0-rc2` |
| lean4checker | `master` (latest) | `v4.25.0-rc2` | N/A |

### Version Mismatches

1. **Lean Toolchain Mismatch**
   - LeanParanoia: `leanprover/lean4:v4.25.0` (stable)
   - Comparator: `leanprover/lean4:v4.25.0-rc2` (release candidate)
   - **Impact**: Minor - rc2 and stable are compatible, but should align versions for consistency

2. **lean4checker Version**
   - LeanParanoia uses: `master` branch (currently at v4.26.0-rc2)
   - Comparator uses: `v4.25.0-rc2` tag
   - **Impact**: LeanParanoia's lean4checker is newer; may need version pinning

## External Dependencies

Comparator requires these tools in `PATH`:

1. **landrun** ([GitHub - Zouuup/landrun](https://github.com/Zouuup/landrun))
   - Linux-only sandboxing tool using Landlock
   - Requires Linux kernel 5.13+ (6.7+ for network restrictions)
   - Install: `go install github.com/zouuup/landrun/cmd/landrun@latest`
   - **Impact**: macOS/Windows incompatible; CI needs Linux runner with modern kernel

2. **lean4export** ([GitHub - leanprover/lean4export](https://github.com/leanprover/lean4export))
   - Exports Lean declarations to external format
   - Must match target Lean version (no release tags; uses toolchain `v4.25.0-rc2`)
   - Must be built separately and available in `PATH`
   - **Impact**: Requires additional build step in test setup

## Methodology Differences

### Comparator's Approach

Comparator is a **challenge-solution verifier**:
- Requires a "Challenge" module with theorem statements (with `sorry`)
- Requires a "Solution" module with proofs
- Compares theorem signatures between environments
- Checks axiom usage against whitelist
- Replays proofs through Lean kernel

### Current Benchmark Methodology

LeanParanoia tests use:
- Pre-compiled exploit files with theorems
- Single module verification per test
- Direct theorem name verification

### Key Differences

| Aspect | LeanParanoia/lean4checker/SafeVerify | Comparator |
|--------|--------------------------------------|------------|
| Input | Single theorem name | Challenge + Solution modules |
| Reference | None needed (or olean for SafeVerify) | Challenge module required |
| Config | CLI arguments | JSON config file |
| Sandbox | None | landrun (Linux Landlock) |
| Export | Direct olean access | lean4export intermediate format |

## Integration Tasks

### 1. Test Infrastructure Changes

```
tests/
├── benchmark/
│   ├── references/           # Existing SafeVerify references
│   ├── comparator_configs/   # NEW: JSON configs per exploit
│   └── test_tool_comparison.py
```

For each exploit, create:
- A JSON config file specifying challenge/solution modules and theorem names
- Challenge files (theorem statements with `sorry`)
- Solution module = existing exploit file

### 2. ComparatorRunner Class

Add to `test_tool_comparison.py`:
```python
class ComparatorRunner:
    def __init__(self, project_path, comparator_binary):
        self.project_path = project_path
        self.comparator_binary = comparator_binary

    def prepare(self, module: str, theorem: str) -> Path:
        """Generate challenge file and config JSON."""
        # Create challenge module with theorem signature + sorry
        # Generate config.json
        # Return config path

    def run(self, module: str, theorem: str) -> Tuple[str, str]:
        """Run comparator on prepared files."""
        config = self.prepare(module, theorem)
        code, output = run_subprocess(
            ["lake", "env", str(self.comparator_binary), str(config)],
            self.project_path
        )
        detected = "no" if code == 0 else ("yes" if code > 0 else "n/a")
        return detected, output
```

### 3. Setup Requirements

```python
@pytest.fixture(scope="session")
def comparator_runner(test_project_path):
    project_path = Path(test_project_path)

    # Install landrun (Linux only)
    if platform.system() != "Linux":
        pytest.skip("Comparator requires Linux (landrun dependency)")

    # Build lean4export
    setup_lean4export()  # Clone, build, add to PATH

    # Add comparator to lakefile
    setup_tool(
        project_path,
        "Comparator",
        "https://github.com/leanprover/comparator.git",
        "main",  # or pin to specific commit
    )

    return ComparatorRunner(project_path, comparator_binary)
```

### 4. Challenge File Generation

For each exploit file, auto-generate challenge file:
```lean
-- Challenge.lean (auto-generated)
import LeanTestProject.SomeModule  -- If needed for dependencies

theorem exploit_theorem : False := sorry  -- Extract signature from solution
```

### 5. CI/Environment Requirements

- **Linux kernel 5.13+** (preferably 6.7+ for full landrun features)
- **Go toolchain** (for installing landrun)
- **landrun binary** in PATH
- **lean4export binary** in PATH (must match Lean version)

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Linux-only (landrun) | Cannot run on macOS CI | Mark as Linux-only, skip on other platforms |
| Lean version drift | Comparator may lag | Pin versions or contribute upstream |
| Challenge generation complexity | May not capture all signatures | Manual challenge files for edge cases |
| lean4export not versioned | Version matching difficult | Build from source with matching toolchain |
| Sandbox overhead | Slower benchmarks | Report both sandboxed and unsandboxed times |

## Recommended Next Steps

1. **Align Lean toolchain versions** - Update LeanParanoia to `v4.25.0` or wait for comparator to update
2. **Create challenge file generator** - Script to extract theorem signatures from exploit files
3. **Add ComparatorRunner** - Implement runner class with proper setup
4. **Linux CI job** - Ensure CI runs on Linux with kernel 5.13+
5. **Build lean4export in setup** - Add build step for lean4export to test fixtures
6. **Pin versions** - Use specific commits/tags for reproducibility

## Open Questions

1. Should comparator be optional (skip if dependencies unavailable)?
2. Should we report sandboxed vs unsandboxed timing separately?
3. How to handle exploits where challenge generation is non-trivial?
4. Should we upstream compatibility improvements to comparator?
