import LeanParanoia
import Lean
import Lean.Data.Json

open Lean Meta LeanParanoia

def parseArgs (args : List String) : IO (VerificationConfig × String) := do
  let mut config := VerificationConfig.default
  let mut theoremName := ""
  let mut i := 0

  while i < args.length do
    let arg := args[i]!
    match arg with
    | "--no-sorry" => config := { config with checkSorry := false }
    | "--no-metavariables" => config := { config with checkMetavariables := false }
    | "--no-unsafe" => config := { config with checkUnsafe := false }
    | "--no-partial" => config := { config with checkPartial := false }
    | "--no-axioms" => config := { config with checkAxioms := false }
    | "--no-extern" => config := { config with checkExtern := false }
    | "--no-implemented-by" => config := { config with checkImplementedBy := false }
    | "--no-csimp" => config := { config with checkCSimp := false }
    | "--no-native-computation" => config := { config with checkNativeComputation := false }
    | "--no-constructors" => config := { config with checkConstructors := false }
    | "--no-recursors" => config := { config with checkRecursors := false }
    | "--no-source-check" => config := { config with checkSource := false }
    | "--no-replay" => config := { config with enableReplay := false }
    | "--no-opaque-bodies" => config := { config with checkOpaqueBodies := false }
    | "--fail-fast" => config := { config with failFast := true }
    | "--allowed-axioms" =>
      i := i + 1
      if i >= args.length then
        throw (IO.userError "--allowed-axioms requires a comma-separated list of axiom names")
      let axiomsStr := args[i]!
      let axioms := axiomsStr.splitOn ","
      config := { config with allowedAxioms := axioms }
    | "--source-blacklist" =>
      i := i + 1
      if i >= args.length then
        throw (IO.userError "--source-blacklist requires a comma-separated list of patterns")
      let patternsStr := args[i]!
      let patterns := patternsStr.splitOn ","
      config := { config with sourceBlacklist := patterns }
    | "--source-whitelist" =>
      i := i + 1
      if i >= args.length then
        throw (IO.userError "--source-whitelist requires a comma-separated list of patterns")
      let patternsStr := args[i]!
      let patterns := patternsStr.splitOn ","
      config := { config with sourceWhitelist := patterns }
    | "--trust-modules" =>
      i := i + 1
      if i >= args.length then
        throw (IO.userError "--trust-modules requires a comma-separated list of module prefixes")
      let modulesStr := args[i]!
      let modules := (modulesStr.splitOn ",").toArray
      config := { config with trustModules := modules }
    | "--help" | "-h" =>
      IO.println "Usage: paranoia [OPTIONS] THEOREM_NAME"
      IO.println ""
      IO.println "Specify theorems using their full module path: Module.SubModule.theorem_name"
      IO.println ""
      IO.println "Options:"
      IO.println "  --no-sorry              Disable sorry check"
      IO.println "  --no-metavariables      Disable metavariable check"
      IO.println "  --no-unsafe             Disable unsafe check"
      IO.println "  --no-partial            Disable partial function check"
      IO.println "  --no-axioms             Disable axiom whitelist check"
      IO.println "  --no-extern             Disable extern check"
      IO.println "  --no-implemented-by     Disable implemented_by check"
      IO.println "  --no-csimp              Disable csimp attribute check"
      IO.println "  --no-native-computation Disable native_decide/ofReduce check"
      IO.println "  --no-constructors       Disable constructor integrity check"
      IO.println "  --no-recursors          Disable recursor integrity check"
      IO.println "  --no-source-check       Disable source-level pattern check"
      IO.println "  --no-replay             Disable environment replay"
      IO.println "  --no-opaque-bodies      Skip inspecting opaque constant bodies"
      IO.println "  --allowed-axioms AXIOMS Comma-separated list of allowed axioms"
      IO.println "                          (default: propext,Quot.sound,Classical.choice)"
      IO.println "  --source-blacklist PATTERNS Comma-separated list of source patterns to reject"
      IO.println "                          (default: 'local instance', 'local notation', etc.)"
      IO.println "  --source-whitelist PATTERNS Comma-separated list of patterns to allow despite blacklist"
      IO.println "  --trust-modules MODULES Comma-separated list of module prefixes to trust"
      IO.println "                          (e.g., Std,Mathlib to skip verification of those dependencies)"
      IO.println "  --fail-fast             Stop after first failing check"
      IO.println "  -h, --help              Show this help"
      throw (IO.userError "")
    | name =>
      if !name.startsWith "--" then
        if theoremName.isEmpty then
          theoremName := name
        else
          throw (IO.userError s!"Multiple theorem names provided: {theoremName} and {name}")
      else
        throw (IO.userError s!"Unknown option: {arg}. Use --help for usage.")
    i := i + 1

  if theoremName.isEmpty then
    throw (IO.userError "Missing theorem name. Use --help for usage.")

  return (config, theoremName)

unsafe def verifyTheorem (config : VerificationConfig) (theoremName : String) : IO VerificationResult := do
  -- Parse the theorem name as a Lean Name
  -- The theorem name should be in full qualified format:
  -- Module.SubModule.theorem_name

  let fullName := theoremName.toName
  let moduleName := fullName.getPrefix

  initSearchPath (← findSysroot)

  -- Try to import the module, catch errors if module doesn't exist or kernel rejected it
  let env ← try
    importModules #[{module := moduleName}] {} 0
  catch e =>
    -- Module import failed (kernel rejection, missing .olean, etc.)
    let failure : CheckFailure := {
      name := "KernelRejection"
      reason := s!"Failed to import module '{moduleName}': {e}"
    }
    return VerificationResult.fromFailures [failure]

  let actualName :=
    if env.find? fullName |>.isSome then
      fullName
    else
      fullName.components.getLast!

  -- Build shared resources once for efficiency
  let csimpCache ← IO.mkRef LeanParanoia.mkCSimpCache
  let sourceCache ← IO.mkRef (Std.HashMap.emptyWithCapacity : LeanParanoia.SourceFileCache)

  let failures ← LeanParanoia.runChecks config env actualName csimpCache sourceCache
  return VerificationResult.fromFailures failures

unsafe def main (args : List String) : IO UInt32 := do
  try
    let (config, theoremName) ← parseArgs args
    let result ← verifyTheorem config theoremName
    IO.println (Lean.toJson result).compress
    let exitCode : UInt32 := if result.success then 0 else 1
    return exitCode
  catch e =>
    if e.toString.isEmpty then
      return (0 : UInt32)  -- Help was shown
    IO.eprintln (e.toString)
    return (1 : UInt32)
