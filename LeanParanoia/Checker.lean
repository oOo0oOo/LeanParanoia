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
  (csimpCache : IO.Ref CSimpCache) (info : ConstantInfo) (allowOpaqueBodies : Bool) : IO (List String) := do
  match ← checkIsCSimp env csimpCache info.name with
  | none => return []
  | some (moduleName, entry) =>
      let moduleStr := moduleName.toString
      if isTrustedConstant env info.name trustModules ||
         isCoreModuleName env info.name ||
         isLeanCoreConstant env info.name ||
         matchesTrustedPrefix moduleStr trustModules then
        return []
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
        return (theoremReasons.toList ++ sourceReasons ++ targetReasons)

def checkNoCSimp (env : Environment) (csimpCache : IO.Ref CSimpCache) (cinfo : ConstantInfo)
    (trustModules : Array String := #[]) (allowOpaqueBodies : Bool := true) : IO (Option CheckFailure) := do
  match ← collectCSimpIssues env trustModules csimpCache cinfo allowOpaqueBodies with
  | [] => return none
  | reasons =>
      let message := String.intercalate "; " reasons
      return some { name := "CSimp", reason := s!"@[csimp] theorem '{cinfo.name}' is unsound: {message}" }

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

def checkGlobalCSimps (env : Environment) (csimpCache : IO.Ref CSimpCache) (trustModules : Array String)
    (allowOpaqueBodies : Bool) : IO (List CheckFailure) := do
  let moduleNames := env.allImportedModuleNames
  let mut failures : List CheckFailure := []

  for modIdx in [:moduleNames.size] do
    let entries := Lean.Compiler.CSimp.ext.ext.getModuleEntries env modIdx
    for entry in entries do
      let data : Lean.Compiler.CSimp.Entry :=
        match entry with
        | ScopedEnvExtension.Entry.global data => data
        | ScopedEnvExtension.Entry.scoped _ data => data

      if let some info := env.find? data.thmName then
        if let some failure ← checkNoCSimp env csimpCache info trustModules allowOpaqueBodies then
          failures := failure :: failures

  return failures

unsafe def runChecks (config : VerificationConfig) (env : Environment) (name : Name)
    (csimpCache : IO.Ref CSimpCache) (sourceCache : IO.Ref SourceFileCache) :
    IO (List CheckFailure) := do
  match env.find? name with
  | none =>
    return [{ name := "KernelRejection", reason := s!"Theorem '{name}' not found in environment" }]
  | some info =>
    let failuresRef ← IO.mkRef #[]
    let allowOpaqueBodies := config.checkOpaqueBodies

    let addFailure (f : CheckFailure) : IO Unit := do
      failuresRef.modify (·.push f)

    let value := (info.value? (allowOpaque := allowOpaqueBodies)).getD (.const name [])

    if config.checkMetavariables then
      if let some failure := checkNoMetavars name value then
        addFailure failure
        if config.failFast then return [failure]

    if config.checkSorry then
      if let some failure := checkNoSorry name value then
        addFailure failure
        if config.failFast then return [failure]

    if config.checkUnsafe then
      if let some failure := checkNoUnsafe info then
        addFailure failure
        if config.failFast then return [failure]

    if config.checkPartial then
      if let some failure := checkNoPartial info then
        addFailure failure
        if config.failFast then return [failure]

    if config.checkExtern then
      if let some failure := checkNoExtern env info config.trustModules then
        addFailure failure
        if config.failFast then return [failure]

    if config.checkImplementedBy then
      if let some failure := checkNoImplementedBy env info config.trustModules then
        addFailure failure
        if config.failFast then return [failure]

    if config.checkCSimp then
      if let some failure ← checkNoCSimp env csimpCache info config.trustModules allowOpaqueBodies then
        addFailure failure
        if config.failFast then return [failure]

    let needsTransitiveDeps := config.checkUnsafe || config.checkPartial || config.checkAxioms ||
                  config.checkSorry || config.checkExtern || config.checkImplementedBy || config.checkCSimp ||
                  config.checkConstructors || config.checkRecursors ||
                  config.checkSource || config.enableReplay || config.checkNativeComputation

    let mut allDeps : NameSet := ∅

    if needsTransitiveDeps then
      let visitor (depName : Name) (depInfo : ConstantInfo) : IO (Option CheckFailure) := do
        if depName == name then
          if config.checkAxioms then
            if isAxiom depInfo then
              let axiomStr := depName.toString
              if !config.allowedAxioms.contains axiomStr then
                let f := { name := "CustomAxioms", reason := s!"Uses disallowed axiom: {axiomStr}" }
                addFailure f
                if config.failFast then return some f
          return none

        if config.checkSorry then
           match depInfo.value? (allowOpaque := allowOpaqueBodies) with
           | some depValue =>
               if hasSorry depValue then
                 let f := { name := "Sorry", reason := s!"Dependency '{depName}' contains sorry" }
                 addFailure f
                 if config.failFast then return some f
           | none => pure ()

        if config.checkUnsafe then
          if let some f := checkNoUnsafe depInfo then
            addFailure f
            if config.failFast then return some f

        if config.checkPartial then
          if let some f := checkNoPartial depInfo then
            addFailure f
            if config.failFast then return some f

        if config.checkExtern then
          if let some f := checkNoExtern env depInfo config.trustModules then
            addFailure f
            if config.failFast then return some f

        if config.checkImplementedBy then
          if let some f := checkNoImplementedBy env depInfo config.trustModules then
            addFailure f
            if config.failFast then return some f

        if config.checkAxioms then
          if isAxiom depInfo then
            let axiomStr := depName.toString
            if !config.allowedAxioms.contains axiomStr then
              let f := { name := "CustomAxioms", reason := s!"Uses disallowed axiom: {axiomStr}" }
              addFailure f
              if config.failFast then return some f

        if config.checkCSimp then
          if let some f ← checkNoCSimp env csimpCache depInfo config.trustModules allowOpaqueBodies then
            addFailure f
            if config.failFast then return some f

        if config.checkSource then
           if let some f ← checkSourcePatterns env depName config.sourceBlacklist config.sourceWhitelist config.trustModules sourceCache then
             addFailure f
             if config.failFast then return some f

        if config.checkRecursors then
           if let some f ← checkRecursorIntegrity env depName then
             addFailure f
             if config.failFast then return some f

        if config.checkConstructors then
           if let some f ← checkConstructorIntegrity env depName then
             addFailure f
             if config.failFast then return some f

        return none

      let (failure?, deps) ← visitTransitiveDeps env name visitor ∅ config.trustModules allowOpaqueBodies
      allDeps := deps

      if let some f := failure? then
        return [f]

    if config.checkNativeComputation then
      if let some failure := checkNoNativeComputation name value allDeps then
        addFailure failure
        if config.failFast then return [failure]

    if config.checkCSimp then
      let currentFailures ← failuresRef.get
      if currentFailures.isEmpty || !config.failFast then
        let globalFailures ← checkGlobalCSimps env csimpCache config.trustModules allowOpaqueBodies
        for f in globalFailures do
          addFailure f
          if config.failFast then return [f]

    if config.checkSource then
      if let some failure ← checkSourcePatterns env name config.sourceBlacklist config.sourceWhitelist config.trustModules sourceCache then
        addFailure failure
        if config.failFast then return [failure]

    if config.enableReplay then
      if let some failure ← checkEnvironmentReplay env allDeps config.trustModules then
        addFailure failure
        if config.failFast then return [failure]

    return (← failuresRef.get).toList

end LeanParanoia
