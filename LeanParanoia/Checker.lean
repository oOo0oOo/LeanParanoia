import Lean
import Lean.Compiler.ExportAttr
import Lean.Compiler.ImplementedByAttr
import Lean.Compiler.InitAttr
import Lean.Data.Json
import Lean4Checker.Replay
import LeanParanoia.Config
import LeanParanoia.Helpers

open Lean Meta Elab Std

namespace LeanParanoia

structure CheckFailure where
  name : String
  reason : String
deriving Repr, BEq

structure VerificationResult where
  success : Bool
  failures : List (String × List String)
  errorTrace : Option String := none
deriving Repr

def VerificationResult.fromFailures (failures : List CheckFailure) : VerificationResult :=
  let grouped := failures.foldl (init := []) fun acc f =>
    match acc.find? (·.1 == f.name) with
    | some (_, msgs) => acc.replace (f.name, msgs) (f.name, msgs ++ [f.reason])
    | none => acc ++ [(f.name, [f.reason])]
  { success := failures.isEmpty, failures := grouped }

instance : ToJson VerificationResult where
  toJson r :=
    let failuresJson := Json.mkObj <| r.failures.map fun (check, msgs) =>
      (check, Json.arr (msgs.map Json.str).toArray)
    let fields := [("success", Json.bool r.success), ("failures", failuresJson)]
    Json.mkObj <| r.errorTrace.map (fun t => fields ++ [("errorTrace", Json.str t)]) |>.getD fields

def checkNoSorry (name : Name) (e : Expr) : Option CheckFailure :=
  if hasSorry e then
    some { name := "Sorry", reason := s!"Theorem '{name}' contains sorry" }
  else
    none

def checkNoMetavars (name : Name) (e : Expr) : Option CheckFailure :=
  if e.hasMVar then
    some { name := "Metavariables", reason := s!"Theorem '{name}' contains unresolved metavariables" }
  else
    none

def checkNoUnsafe (cinfo : ConstantInfo) : Option CheckFailure :=
  if cinfo.isUnsafe then
    some { name := "Unsafe", reason := s!"Definition '{cinfo.name}' is marked unsafe" }
  else
    none

def checkNoPartial (cinfo : ConstantInfo) : Option CheckFailure :=
  if cinfo.isPartial then
    some { name := "Partial", reason := s!"Definition '{cinfo.name}' is marked partial" }
  else
    none

def checkNoExtern (env : Environment) (cinfo : ConstantInfo) (trustModules : Array String := #[]) : Option CheckFailure :=
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
      some { name := "Extern", reason := s!"Definition '{cinfo.name}' has dangerous {attrKind} attribute" }
    else
      none

def checkNoImplementedBy (env : Environment) (cinfo : ConstantInfo)
    (trustModules : Array String := #[]) : Option CheckFailure :=
  match Lean.Compiler.implementedByAttr.getParam? env cinfo.name with
  | none => none
  | some implName =>
    if shouldSkipTrustedConstant env cinfo.name trustModules ||
       shouldSkipTrustedConstant env implName trustModules then
      none
    else
      some { name := "ImplementedBy", reason := s!"Definition '{cinfo.name}' uses implemented_by target '{implName}' " }

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

          if let some f := checkNoImplementedBy env info trustModules then
            acc := acc.push s!"{label} constant '{name}': {f.reason}"

          if let some f := checkNoExtern env info trustModules then
            acc := acc.push s!"{label} constant '{name}': {f.reason}"

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
    (trustModules : Array String := #[]) (allowOpaqueBodies : Bool := true) : Option CheckFailure :=
  match collectCSimpIssues env trustModules csimpMap cinfo allowOpaqueBodies with
  | [] => none
  | reasons =>
      let message := String.intercalate "; " reasons
      some { name := "CSimp", reason := s!"@[csimp] theorem '{cinfo.name}' is unsound: {message}" }

def collectAllDangerousCSimps (env : Environment) (csimpMap : CSimpEntryMap)
    (trustModules : Array String := #[]) (checked : Std.HashSet Name := {})
    (allowOpaqueBodies : Bool := true) : List CheckFailure :=
  (csimpMap.toList.foldl (init := []) fun acc (thmName, _) =>
    if checked.contains thmName then
      acc
    else
      match env.find? thmName with
      | none => acc
      | some thmInfo =>
          match checkNoCSimp env csimpMap thmInfo trustModules allowOpaqueBodies with
          | some failure => failure :: acc
          | none => acc).reverse

def checkConstructorIntegrity (env : Environment) (name : Name) : IO (Option CheckFailure) := do
  match env.find? name with
  | none => return none
  | some info =>
    match info with
    | .inductInfo val =>
      if isBuiltinInductive name then
        return none
      let constructors := val.ctors
      if constructors.isEmpty then
        return some { name := "ConstructorIntegrity", reason := s!"Inductive '{name}' has no constructors" }
      else
        return none
    | _ => return none

def checkRecursorIntegrity (env : Environment) (name : Name) : IO (Option CheckFailure) := do
  match env.find? name with
  | none => return none
  | some info =>
    match info with
    | .inductInfo val =>
      if isBuiltinInductive name then
        return none
      if val.ctors.isEmpty then
        return some { name := "RecursorIntegrity", reason := s!"Inductive '{name}' has no constructors to justify recursor" }
      let recursorName := name ++ `rec
      match env.find? recursorName with
      | none =>
        return some { name := "RecursorIntegrity", reason := s!"Inductive '{name}' is missing recursor" }
      | some _recursorInfo =>
        return none
    | _ => return none

def checkNoNativeComputation (name : Name) (value : Expr) (deps : NameSet) : Option CheckFailure :=
  match findNativeComputationInExpr? value with
  | some nativeConst =>
      some { name := "NativeComputation"
           , reason := s!"Definition '{name}' uses native computation primitive '{nativeConst}'" }
  | none =>
      match findNativeComputationInDeps deps name with
      | some nativeConst =>
          some { name := "NativeComputation"
               , reason := s!"Definition '{name}' depends on native computation primitive '{nativeConst}'" }
      | none => none

def checkSourcePatterns (env : Environment) (name : Name) (blacklist whitelist : List String)
    (trustModules : Array String := #[]) (sourceCache : IO.Ref SourceFileCache) : IO (Option CheckFailure) := do
  let some moduleName := getConstantModule env name | return none
  if isTrustedModuleName moduleName trustModules then return none
  if isCoreModuleName env name || isLeanCoreConstant env name then return none

  let patterns := blacklist.filter (!whitelist.contains ·)
  let some sourceFile ← findSourceFile env moduleName | return none

  let lines ← readSourceFileCached sourceCache sourceFile
  if lines.isEmpty then return none

  let mut found : Array String := #[]

  for h : i in [:lines.size] do
    let line := lines[i]
    if line.trim.startsWith "--" then continue

    for pattern in patterns do
      if (line.splitOn pattern).length > 1 then
        found := found.push s!"Line {i + 1}: {pattern}"

  if found.isEmpty then return none
  return some { name := "SourcePatterns", reason := s!"Source file contains blacklisted patterns: {String.intercalate ", " found.toList}" }

unsafe def checkEnvironmentReplay (env : Environment) (allDeps : NameSet) (trustModules : Array String := #[]) : IO (Option CheckFailure) := do
  try
    let modulesToReplay := collectModulesToReplay env allDeps trustModules
    if modulesToReplay.isEmpty then
      return none

    for modName in modulesToReplay do
      let mFile ← findOLean modName
      unless (← mFile.pathExists) do
        return some { name := "Replay"
                    , reason := s!"Object file '{mFile}' of module {modName} does not exist" }

      let (mod, region) ← readModuleData mFile
      let (_, s) ← importModulesCore mod.imports |>.run
      let baseEnv ← finalizeImport s #[{module := modName}] {} 0 false false

      let mut newConstants : Std.HashMap Name ConstantInfo := ∅
      for constName in mod.constNames, ci in mod.constants do
        newConstants := newConstants.insert constName ci

      let _ ← baseEnv.replay' newConstants
      baseEnv.freeRegions
      region.free

    return none
  catch e =>
    return some { name := "Replay", reason := s!"Replay verification failed: {e}" }

unsafe def runChecks (config : VerificationConfig) (env : Environment) (name : Name)
    (csimpMap : CSimpEntryMap := Std.HashMap.emptyWithCapacity) (sourceCache : IO.Ref SourceFileCache) :
    IO (List CheckFailure) := do
  match env.find? name with
  | none =>
    return [{ name := "KernelRejection", reason := s!"Theorem '{name}' not found in environment" }]
  | some info =>
    let mut failures : Array CheckFailure := #[]
    let allowOpaqueBodies := config.checkOpaqueBodies

    let value := (info.value? (allowOpaque := allowOpaqueBodies)).getD (.const name [])

    if config.checkMetavariables then
      if let some failure := checkNoMetavars name value then
        failures := failures.push failure
        if config.failFast then
          return failures.toList

    if config.checkSorry then
      if let some failure := checkNoSorry name value then
        failures := failures.push failure
        if config.failFast then
          return failures.toList

    if config.checkUnsafe then
      if let some failure := checkNoUnsafe info then
        failures := failures.push failure
        if config.failFast then
          return failures.toList

    if config.checkPartial then
      if let some failure := checkNoPartial info then
        failures := failures.push failure
        if config.failFast then
          return failures.toList

    if config.checkExtern then
      if let some failure := checkNoExtern env info config.trustModules then
        failures := failures.push failure
        if config.failFast then
          return failures.toList

    if config.checkImplementedBy then
      if let some failure := checkNoImplementedBy env info config.trustModules then
        failures := failures.push failure
        if config.failFast then
          return failures.toList

    let needsTransitiveDeps := config.checkUnsafe || config.checkPartial || config.checkAxioms ||
                  config.checkSorry || config.checkExtern || config.checkImplementedBy || config.checkCSimp ||
                  config.checkConstructors || config.checkRecursors ||
                  config.checkSource || config.enableReplay || config.checkNativeComputation

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

    if config.checkNativeComputation then
      if let some failure := checkNoNativeComputation name value allDeps then
        failures := failures.push failure
        if config.failFast then
          return failures.toList

    if config.checkAxioms then
      let mut disallowed : Array String := #[]
      for (depName, depInfo) in depInfos do
        if isAxiom depInfo then
          let axiomStr := depName.toString
          if !config.allowedAxioms.contains axiomStr then
            disallowed := disallowed.push axiomStr
            if config.failFast then
              let failure : CheckFailure :=
                { name := "CustomAxioms", reason := s!"Uses disallowed axioms: {String.intercalate ", " disallowed.toList}" }
              return [failure]

      if !disallowed.isEmpty then
        let failure : CheckFailure :=
          { name := "CustomAxioms", reason := s!"Uses disallowed axioms: {String.intercalate ", " disallowed.toList}" }
        failures := failures.push failure
        if config.failFast then
          return failures.toList
    let mut checkedCSimps : Std.HashSet Name := Std.HashSet.emptyWithCapacity

    if config.checkCSimp && (failures.isEmpty || !config.failFast) then
      if let some failure := checkNoCSimp env csimpMap info config.trustModules allowOpaqueBodies then
        failures := failures.push failure
        if config.failFast then
          return failures.toList
      if csimpMap.contains info.name then
        checkedCSimps := checkedCSimps.insert info.name

    if needsTransitiveDeps && (failures.isEmpty || !config.failFast) then
      let optionChecks : List (Name → ConstantInfo → Option CheckFailure) :=
        let base : List (Name → ConstantInfo → Option CheckFailure) := []
        let base :=
          if config.checkSorry then
            (fun depName depInfo =>
              match depInfo.value? (allowOpaque := allowOpaqueBodies) with
              | some depValue =>
                  if hasSorry depValue then
                    some { name := "Sorry", reason := s!"Dependency '{depName}' contains sorry" }
                  else
                    none
              | none => none) :: base
          else
            base
        let base :=
          if config.checkCSimp then
            (fun _ info => checkNoCSimp env csimpMap info config.trustModules allowOpaqueBodies) :: base
          else
            base
        let base :=
          if config.checkImplementedBy then
            (fun _ info => checkNoImplementedBy env info config.trustModules) :: base
          else
            base
        let base :=
          if config.checkExtern then
            (fun _ info => checkNoExtern env info config.trustModules) :: base
          else
            base
        let base := if config.checkUnsafe then (fun _ info => checkNoUnsafe info) :: base else base
        let base := if config.checkPartial then (fun _ info => checkNoPartial info) :: base else base
        base.reverse

      let ioChecks : List (Name → IO (Option CheckFailure)) :=
        let base : List (Name → IO (Option CheckFailure)) := []
        let base := if config.checkSource then (fun depName => checkSourcePatterns env depName config.sourceBlacklist config.sourceWhitelist config.trustModules sourceCache) :: base else base
        let base := if config.checkRecursors then (fun depName => checkRecursorIntegrity env depName) :: base else base
        let base := if config.checkConstructors then (fun depName => checkConstructorIntegrity env depName) :: base else base
        base.reverse

      for (depName, depInfo) in depInfos do
        if depName == name || skipConst depName then
          continue

        for checkFn in optionChecks do
          if let some failure := checkFn depName depInfo then
            failures := failures.push failure
            if config.failFast then
              return failures.toList

        if config.checkCSimp && csimpMap.contains depInfo.name then
          checkedCSimps := checkedCSimps.insert depInfo.name

        for checkFn in ioChecks do
          if let some failure ← checkFn depName then
            failures := failures.push failure
            if config.failFast then
              return failures.toList

    if config.checkCSimp && (failures.isEmpty || !config.failFast) then
      let csimpFailures := collectAllDangerousCSimps env csimpMap config.trustModules checkedCSimps allowOpaqueBodies
      for failure in csimpFailures do
        failures := failures.push failure
        if config.failFast then
          return failures.toList

    if config.checkSource && (failures.isEmpty || !config.failFast) then
      if let some failure ← checkSourcePatterns env name config.sourceBlacklist config.sourceWhitelist config.trustModules sourceCache then
        failures := failures.push failure
        if config.failFast then
          return failures.toList

    if config.enableReplay && (failures.isEmpty || !config.failFast) then
      if let some failure ← checkEnvironmentReplay env allDeps config.trustModules then
        failures := failures.push failure
        if config.failFast then
          return failures.toList

    return failures.toList

end LeanParanoia
