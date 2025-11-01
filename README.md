# LeanParanoia

> **THIS TOOL IS STILL IN EARLY DEVELOPMENT AND NOT READY FOR USE!**

Configurable proof verification for Lean 4 that detects soundness exploits through dependency analysis and environment replay via [lean4checker](https://github.com/leanprover/lean4checker). Operates without trusted reference files and cannot guarantee complete soundness. Validate critical proofs with challenge–solution verifiers.

## Exploits

See [EXPLOITS.md](EXPLOITS.md) for a list of the different exploit categories that LeanParanoia checks for.

## Installation & Usage

Add the LeanParanoia dependency to your `lakefile.toml`:

```toml
[[require]]
name = "paranoia"
git = "https://github.com/oOo0oOo/LeanParanoia"
rev = "main"
```

Then, in your terminal, run:

```bash
lake update --keep-toolchain
lake build paranoia
lake exe paranoia MyTheoremName # Use Module.SubModule.theorem_name
```

## Command Line Options

```
Usage: paranoia [OPTIONS] THEOREM_NAME

Specify theorems using their full module path: Module.SubModule.theorem_name

Options:
  --no-sorry              Disable sorry check
  --no-metavariables      Disable metavariable check
  --no-unsafe             Disable unsafe check
  --no-partial            Disable partial function check
  --no-axioms             Disable axiom whitelist check
  --no-extern             Disable extern check
  --no-implemented-by     Disable implemented_by check
  --no-csimp              Disable csimp attribute check
  --no-native-computation Disable native_decide/ofReduce check
  --no-constructors       Disable constructor integrity check
  --no-recursors          Disable recursor integrity check
  --no-source-check       Disable source-level pattern check
  --no-replay             Disable environment replay
  --no-opaque-bodies      Skip inspecting opaque constant bodies
  --allowed-axioms AXIOMS Comma-separated list of allowed axioms
                          (default: propext,Quot.sound,Classical.choice)
  --source-blacklist PATTERNS Comma-separated list of source patterns to reject
                          (default: 'local instance', 'local notation', etc.)
  --source-whitelist PATTERNS Comma-separated list of patterns to allow despite blacklist
  --trust-modules MODULES Comma-separated list of module prefixes to trust
                          (e.g., Std,Mathlib to skip verification of those dependencies)
  --fail-fast             Stop after first failing check
  -h, --help              Show this help
```

## Related Projects

- [lean4checker](https://github.com/leanprover/lean4checker): Recheck a compiled Lean olean file using the Lean kernel. **Direct dependency**
- [SaveVerify](https://github.com/GasStationManager/SafeVerify): Check whether a file of submitted Lean code and/or proof matches the specifications.
- [Lean 4 Autograder](https://github.com/robertylewis/lean4-autograder-main): Lean 4 autograder that works with Gradescope.

## Testing

Comprehensive integration tests using pytest:

```bash
uv sync
uv run pytest tests/
```

## License

[MIT License](LICENSE)