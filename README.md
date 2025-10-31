# LeanParanoia

> **THIS TOOL IS STILL IN EARLY DEVELOPMENT AND NOT READY FOR USE!**

Configurable proof verification for Lean 4 that detects soundness exploits through dependency analysis and environment replay via lean4checker. Operates without a trusted reference file, trading security for flexibility, and is best used in combination with challenge-solution verifiers for high-stakes proofs.

## Exploits

See [EXPLOITS.md](EXPLOITS.md) for a list of the different exploit categories that LeanParanoia checks for.

## Installation & Usage

```bash
lake add paranoia https://github.com/oOo0oOo/LeanParanoia
lake build paranoia
lake env .lake/packages/paranoia/.lake/build/bin/paranoia MyTheoremName
```

## Command Line Options

```
Usage: paranoia [OPTIONS] THEOREM_NAME

Options:
  --no-sorry              Disable sorry check
  --no-metavariables      Disable metavariable check
  --no-unsafe             Disable unsafe check
  --no-axioms             Disable axiom whitelist check
  --no-extern             Disable extern check
  --no-opaque-bodies      Skip inspecting opaque constant bodies
  --no-constructors       Disable constructor integrity check
  --no-recursors          Disable recursor integrity check
  --no-source-check       Disable source-level pattern check
  --no-replay             Disable environment replay
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

## Testing

Comprehensive integration tests using pytest:

```bash
uv sync
uv run pytest tests/
```

## License

[MIT License](LICENSE)