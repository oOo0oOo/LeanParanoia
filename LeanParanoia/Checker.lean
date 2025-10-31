import Lean
import Lean.Compiler.ExportAttr
import Lean.Compiler.ImplementedByAttr
import Lean.Compiler.InitAttr
import Lean4Checker.Replay
import LeanParanoia.Types
import LeanParanoia.Config
import LeanParanoia.Helpers

open Lean Meta Elab Std

namespace LeanParanoia

def checkNoSorry (name : Name) (e : Expr) : NamedTest :=
  if hasSorry e then
    { name := "NoSorry"
    , result := TestResult.Fail s!"Theorem '{name}' contains sorry" }
  else
    { name := "NoSorry"
    , result := TestResult.Pass }

def checkNoMetavars (name : Name) (e : Expr) : NamedTest :=
  if e.hasMVar then
    { name := "NoMetavars"
    , result := TestResult.Fail s!"Theorem '{name}' contains unresolved metavariables" }
  else
    { name := "NoMetavars"
    , result := TestResult.Pass }

def checkNoUnsafe (cinfo : ConstantInfo) : Option NamedTest :=
  if cinfo.isUnsafe then
    some { name := "NoUnsafe"
         , result := TestResult.Fail s!"Definition '{cinfo.name}' is marked unsafe" }
  else
    none

def checkNoPartial (cinfo : ConstantInfo) : Option NamedTest :=
  if cinfo.isPartial then
    some { name := "NoPartial"
         , result := TestResult.Fail s!"Definition '{cinfo.name}' is marked partial" }
  else
    none

def checkNoExtern (env : Environment) (cinfo : ConstantInfo) (trustModules : Array String := #[]) : Option NamedTest :=
  if shouldSkipTrustedConstant env cinfo.name trustModules then
    none
  else
    let hasExtern := Lean.isExtern env cinfo.name
    let hasExport := (Lean.getExportNameFor? env cinfo.name).isSome
    let hasInit := isIOUnitRegularInitFn env cinfo.name || isIOUnitBuiltinInitFn env cinfo.name || hasInitAttr env cinfo.name
    if hasExtern || hasExport || hasInit then
      let attrKind :=
        if hasExtern && hasExport then "extern/export"
        else if hasExtern then "extern"
        else if hasExport then "export"
        else "init"
      some { name := "NoExtern"
           , result := TestResult.Fail s!"Definition '{cinfo.name}' has dangerous {attrKind} attribute" }
    else
      none

def checkNoImplementedBy (env : Environment) (cinfo : ConstantInfo)
    (trustModules : Array String := #[]) : Option NamedTest :=
  match Lean.Compiler.implementedByAttr.getParam? env cinfo.name with
  | none => none
  | some implName =>
    if shouldSkipTrustedConstant env cinfo.name trustModules ||
       shouldSkipTrustedConstant env implName trustModules then
      none
    else
      some { name := "NoImplementedBy"
           , result := TestResult.Fail s!"Definition '{cinfo.name}' uses implemented_by target '{implName}' " }

def analyzeConstantForCSimp (env : Environment) (trustModules : Array String)
    (label : String) (name : Name) (allowOpaqueBodies : Bool) : List String :=
  match env.find? name with
  | none => [s!"{label} constant '{name}' was not found"]
  | some info =>
      if shouldSkipTrustedConstant env name trustModules then
        []
      else
        let reasons := Id.run do
          let mut acc : Array String := #[]
          if info.isUnsafe then
            acc := acc.push s!"{label} constant '{name}' is marked unsafe"
          if info.isPartial then
            acc := acc.push s!"{label} constant '{name}' is marked partial"

          match info.value? (allowOpaque := allowOpaqueBodies) with
          | none => acc := acc.push s!"{label} constant '{name}' is an axiom"
          | some val =>
              if hasSorry val then
                acc := acc.push s!"{label} constant '{name}' contains sorry"

          match checkNoImplementedBy env info trustModules with
          | some test =>
            match test.result with
            | TestResult.Fail msg => acc := acc.push s!"{label} constant '{name}': {msg}"
            | _ => ()
          | none => ()

          match checkNoExtern env info trustModules with
          | some test =>
            match test.result with
            | TestResult.Fail msg => acc := acc.push s!"{label} constant '{name}': {msg}"
            | _ => ()
          | none => ()

          return acc
        reasons.toList

def collectCSimpIssues (env : Environment) (trustModules : Array String)
  (csimpMap : CSimpEntryMap) (info : ConstantInfo) (allowOpaqueBodies : Bool) : List String :=
  match csimpEntry? csimpMap info.name with
  | none => []
  | some (moduleName, entry) =>
      let moduleStr := moduleName.toString
      if isTrustedConstant env info.name trustModules ||
         isCoreModuleName env info.name ||
         isLeanCoreConstant env info.name ||
         matchesTrustedPrefix moduleStr trustModules then
        []
      else
        let theoremReasons := Id.run do
          let mut acc : Array String := #[]
          if info.isUnsafe then
            acc := acc.push "the theorem is marked unsafe"
          if info.isPartial then
            acc := acc.push "the theorem is marked partial"
          match info.value? (allowOpaque := allowOpaqueBodies) with
          | none => acc := acc.push "the theorem is an axiom"
          | some val =>
              if hasSorry val then
                acc := acc.push "the theorem contains sorry"
          return acc

        let sourceReasons := analyzeConstantForCSimp env trustModules "source" entry.fromDeclName allowOpaqueBodies
        let targetReasons := analyzeConstantForCSimp env trustModules "target" entry.toDeclName allowOpaqueBodies
        (theoremReasons.toList ++ sourceReasons ++ targetReasons)

def checkNoCSimp (env : Environment) (csimpMap : CSimpEntryMap) (cinfo : ConstantInfo)
    (trustModules : Array String := #[]) (allowOpaqueBodies : Bool := true) : Option NamedTest :=
  match collectCSimpIssues env trustModules csimpMap cinfo allowOpaqueBodies with
  | [] => none
  | reasons =>
      let message := String.intercalate "; " reasons
      some { name := "NoCSimp"
           , result := TestResult.Fail s!"@[csimp] theorem '{cinfo.name}' is unsound: {message}" }

def collectAllDangerousCSimps (env : Environment) (csimpMap : CSimpEntryMap)
    (trustModules : Array String := #[]) (checked : Std.HashSet Name := {})
    (allowOpaqueBodies : Bool := true) : List NamedTest :=
  (csimpMap.toList.foldl (init := []) fun acc (thmName, _) =>
    if checked.contains thmName then
      acc
    else
      match env.find? thmName with
      | none => acc
      | some thmInfo =>
          match checkNoCSimp env csimpMap thmInfo trustModules allowOpaqueBodies with
          | some test => test :: acc
          | none => acc).reverse

def checkConstructorIntegrity (env : Environment) (name : Name) : IO (Option NamedTest) := do
  match env.find? name with
  | none => return none
  | some info =>
    match info with
    | .inductInfo val =>
      if isBuiltinInductive name then
        return none
      let constructors := val.ctors
      if constructors.isEmpty then
        return some { name := "ConstructorIntegrity"
                    , result := TestResult.Fail s!"Inductive '{name}' has no constructors" }
      else
        return none
    | _ => return none

def checkRecursorIntegrity (env : Environment) (name : Name) : IO (Option NamedTest) := do
  match env.find? name with
  | none => return none
  | some info =>
    match info with
    | .inductInfo val =>
      if isBuiltinInductive name then
        return none
      if val.ctors.isEmpty then
        return some { name := "RecursorIntegrity"
                    , result := TestResult.Fail s!"Inductive '{name}' has no constructors to justify recursor" }
      let recursorName := name ++ `rec
      match env.find? recursorName with
      | none =>
        return some { name := "RecursorIntegrity"
                    , result := TestResult.Fail s!"Inductive '{name}' is missing recursor" }
      | some _recursorInfo =>
        return none
    | _ => return none

def checkNoNativeComputation (name : Name) (value : Expr) (deps : NameSet) : Option NamedTest :=
  match findNativeComputationInExpr? value with
  | some nativeConst =>
      some { name := "NoNativeComputation"
           , result := TestResult.Fail
               s!"Definition '{name}' uses native computation primitive '{nativeConst}'" }
  | none =>
      match findNativeComputationInDeps deps name with
      | some nativeConst =>
          some { name := "NoNativeComputation"
               , result := TestResult.Fail
                   s!"Definition '{name}' depends on native computation primitive '{nativeConst}'" }
      | none => none

def checkSourcePatterns (env : Environment) (name : Name) (blacklist whitelist : List String)
    (trustModules : Array String := #[]) : IO (Option NamedTest) := do
  let some moduleName := getConstantModule env name | return none
  if isTrustedModuleName moduleName trustModules then return none
  if isCoreModuleName env name || isLeanCoreConstant env name then return none

  let patterns := blacklist.filter (!whitelist.contains ·)
  let some sourceFile ← findSourceFile env moduleName | return none

  if !(← sourceFile.pathExists) then return none

  let lines := (← IO.FS.readFile sourceFile).splitOn "\n"
  let mut found : Array String := #[]

  for h : i in [:lines.length] do
    let line := lines[i]
    if line.trim.startsWith "--" then continue

    for pattern in patterns do
      if (line.splitOn pattern).length > 1 then
        found := found.push s!"Line {i + 1}: {pattern}"

  if found.isEmpty then return none
  return some { name := "SourceCheck"
              , result := TestResult.Fail s!"Source file contains blacklisted patterns: {String.intercalate ", " found.toList}" }

unsafe def checkEnvironmentReplay (env : Environment) (allDeps : NameSet) (trustModules : Array String := #[]) : IO NamedTest := do
  try
    let modulesToReplay := collectModulesToReplay env allDeps trustModules
    if modulesToReplay.isEmpty then
      return { name := "EnvironmentReplay"
             , result := TestResult.Pass }

    for modName in modulesToReplay do
      let mFile ← findOLean modName
      unless (← mFile.pathExists) do
        return { name := "EnvironmentReplay"
               , result := TestResult.Fail s!"Object file '{mFile}' of module {modName} does not exist" }

      let (mod, region) ← readModuleData mFile
      let (_, s) ← importModulesCore mod.imports |>.run
      let baseEnv ← finalizeImport s #[{module := modName}] {} 0 false false

      let mut newConstants : Std.HashMap Name ConstantInfo := ∅
      for constName in mod.constNames, ci in mod.constants do
        newConstants := newConstants.insert constName ci

      let _ ← baseEnv.replay' newConstants
      baseEnv.freeRegions
      region.free

    return { name := "EnvironmentReplay"
           , result := TestResult.Pass }
  catch e =>
    return { name := "EnvironmentReplay"
           , result := TestResult.Fail s!"Replay verification failed: {e}" }

unsafe def runChecks (config : VerificationConfig) (env : Environment) (name : Name) :
    IO (List NamedTest) := do
  match env.find? name with
  | none =>
    return [{ name := "KernelTypeCheck"
            , result := TestResult.Fail s!"Theorem '{name}' not found in environment" }]
  | some info =>
    let mut tests : Array NamedTest := #[]
    let allowOpaqueBodies := config.checkOpaqueBodies

    let csimpMap : CSimpEntryMap :=
      if config.checkExtern then
        buildCSimpEntryMap env
      else
        Std.HashMap.emptyWithCapacity
    let mut checkedCSimps : Std.HashSet Name := Std.HashSet.emptyWithCapacity

    let value := (info.value? (allowOpaque := allowOpaqueBodies)).getD (.const name [])

    if config.checkMetavariables then
      let test := checkNoMetavars name value
      tests := tests.push test
      if config.failFast && !test.result.isPass then
        return tests.toList

    if config.checkUnsafe then
      if let some test := checkNoUnsafe info then
        tests := tests.push test
        if config.failFast && !test.result.isPass then
          return tests.toList

    if config.checkSorry then
      let test := checkNoSorry name value
      tests := tests.push test
      if config.failFast && !test.result.isPass then
        return tests.toList

    if config.checkExtern then
      if let some test := checkNoExtern env info config.trustModules then
        tests := tests.push test
        if config.failFast && !test.result.isPass then
          return tests.toList
      if let some test := checkNoImplementedBy env info config.trustModules then
        tests := tests.push test
        if config.failFast && !test.result.isPass then
          return tests.toList
      if let some test := checkNoCSimp env csimpMap info config.trustModules allowOpaqueBodies then
        tests := tests.push test
        if config.failFast && !test.result.isPass then
          return tests.toList
      if csimpMap.contains info.name then
        checkedCSimps := checkedCSimps.insert info.name

    if config.checkSource then
      if let some test ← checkSourcePatterns env name config.sourceBlacklist config.sourceWhitelist config.trustModules then
        tests := tests.push test
        if config.failFast && !test.result.isPass then
          return tests.toList

    let needsTransitiveDeps := config.checkUnsafe || config.checkAxioms ||
                  config.checkSorry || config.checkExtern ||
                  config.checkConstructors || config.checkRecursors ||
                  config.checkSource || config.enableReplay
    let skipConst := shouldSkipConstant env config.trustModules

    let (allDeps, depInfos, _missingDeps) :=
      if needsTransitiveDeps then
        let deps := collectTransitiveDeps env name ∅ config.trustModules allowOpaqueBodies
        let depList := deps.toList
        let (infoArray, missingRev) := depList.foldl
          (fun (acc : Array (Name × ConstantInfo) × List String) depName =>
            let (arr, miss) := acc
            match env.find? depName with
            | some info => (arr.push (depName, info), miss)
            | none => (arr, depName.toString :: miss))
          (Array.mkEmpty depList.length, ([] : List String))
        (deps, infoArray, missingRev.reverse)
      else
        (∅, #[], [])

    if let some test := checkNoNativeComputation name value allDeps then
      tests := tests.push test
      if config.failFast && !test.result.isPass then
        return tests.toList

    if needsTransitiveDeps then
      let optionChecks : List (Name → ConstantInfo → Option NamedTest) :=
        let base : List (Name → ConstantInfo → Option NamedTest) := []
        let base :=
          if config.checkSorry then
            (fun depName depInfo =>
              match depInfo.value? (allowOpaque := allowOpaqueBodies) with
              | some depValue =>
                  if hasSorry depValue then
                    some { name := "NoSorry"
                         , result := TestResult.Fail s!"Dependency '{depName}' contains sorry" }
                  else
                    none
              | none => none) :: base
          else
            base
        let base :=
          if config.checkExtern then
            (fun _ info => checkNoCSimp env csimpMap info config.trustModules allowOpaqueBodies) ::
            (fun _ info => checkNoImplementedBy env info config.trustModules) ::
            (fun _ info => checkNoExtern env info config.trustModules) :: base
          else
            base
        let base := if config.checkUnsafe then (fun _ info => checkNoUnsafe info) :: base else base
        base.reverse

      let ioChecks : List (Name → IO (Option NamedTest)) :=
        let base : List (Name → IO (Option NamedTest)) := []
        let base := if config.checkSource then (fun depName => checkSourcePatterns env depName config.sourceBlacklist config.sourceWhitelist config.trustModules) :: base else base
        let base := if config.checkRecursors then (fun depName => checkRecursorIntegrity env depName) :: base else base
        let base := if config.checkConstructors then (fun depName => checkConstructorIntegrity env depName) :: base else base
        base.reverse

      for (depName, depInfo) in depInfos do
        if depName == name || skipConst depName then
          continue

        for checkFn in optionChecks do
          if let some test := checkFn depName depInfo then
            tests := tests.push test
            if config.failFast && !test.result.isPass then
              return tests.toList

        if config.checkExtern && csimpMap.contains depInfo.name then
          checkedCSimps := checkedCSimps.insert depInfo.name

        for checkFn in ioChecks do
          if let some test ← checkFn depName then
            tests := tests.push test
            if config.failFast && !test.result.isPass then
              return tests.toList

    if config.checkAxioms then
      let mut disallowed : Array String := #[]
      for (depName, depInfo) in depInfos do
        if isAxiom depInfo then
          let axiomStr := depName.toString
          if !config.allowedAxioms.contains axiomStr then
            disallowed := disallowed.push axiomStr

      let test : NamedTest :=
        if disallowed.isEmpty then
          { name := "AxiomWhitelist", result := TestResult.Pass }
        else
          { name := "AxiomWhitelist"
          , result := TestResult.Fail s!"Uses disallowed axioms: {String.intercalate ", " disallowed.toList}" }
      tests := tests.push test
      if config.failFast && !test.result.isPass then
        return tests.toList

    if config.checkExtern then
      let csimpTests := collectAllDangerousCSimps env csimpMap config.trustModules checkedCSimps allowOpaqueBodies
      for test in csimpTests do
        tests := tests.push test
        if config.failFast && !test.result.isPass then
          return tests.toList

    if config.enableReplay then
      let test ← checkEnvironmentReplay env allDeps config.trustModules
      tests := tests.push test
      if config.failFast && !test.result.isPass then
        return tests.toList

    return tests.toList

end LeanParanoia
