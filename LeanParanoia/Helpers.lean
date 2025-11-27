import Lean
import Lean.Compiler.CSimpAttr
import LeanParanoia.Config

open Lean Meta Elab Std

namespace LeanParanoia

def getConstantModule (env : Environment) (name : Name) : Option Name :=
  env.getModuleIdxFor? name >>= fun idx => env.allImportedModuleNames[idx.toNat]?

def matchesTrustedPrefix (moduleStr : String) (trustModules : Array String) : Bool :=
  trustModules.any fun pref =>
    moduleStr == pref || (moduleStr.startsWith pref && String.Pos.Raw.get! moduleStr ⟨pref.length⟩ == '.')

def nativeComputationPrefixes : Array String :=
  #["Lean.ofReduce", "Lean.reduce", "Lean.nativeDecide", "Lean.trustCompiler"]

def isNativeComputationName (name : Name) : Bool :=
  let str := name.toString
  nativeComputationPrefixes.any (str.startsWith ·)

partial def foldExpr {α : Type} (f : α → Expr → α) (init : α) (e : Expr) : α :=
  let rec loop (worklist : List Expr) (acc : α) : α :=
    match worklist with
    | [] => acc
    | expr :: rest =>
      let acc := f acc expr
      match expr with
      | .app fn a => loop (fn :: a :: rest) acc
      | .lam _ t b _ => loop (t :: b :: rest) acc
      | .forallE _ t b _ => loop (t :: b :: rest) acc
      | .letE _ t v b _ => loop (t :: v :: b :: rest) acc
      | .mdata _ e => loop (e :: rest) acc
      | .proj _ _ e => loop (e :: rest) acc
      | _ => loop rest acc
  loop [e] init

def findNativeComputationInExpr? (e : Expr) : Option Name :=
  foldExpr (fun acc expr => acc.orElse fun _ =>
    match expr with
    | .const name _ => if isNativeComputationName name then some name else none
    | _ => none) none e

def isTrustedModuleName (modName : Name) (trustModules : Array String) : Bool :=
  matchesTrustedPrefix modName.toString trustModules

def isTrustedConstant (env : Environment) (name : Name) (trustModules : Array String) : Bool :=
  let modName := (getConstantModule env name).getD name
  isTrustedModuleName modName trustModules

@[inline] def shouldSkipConstant (env : Environment) (trustModules : Array String) (name : Name) : Bool :=
  isTrustedConstant env name trustModules

def moduleRoot (name : Name) : Name :=
  match name with
  | .str .anonymous s => .str .anonymous s
  | .str parent _ => moduleRoot parent
  | .num .anonymous v => .num .anonymous v
  | .num parent _ => moduleRoot parent
  | .anonymous => .anonymous

def isCoreModuleName (env : Environment) (name : Name) : Bool :=
  match getConstantModule env name with
  | none => false
  | some moduleName =>
    let root := moduleRoot moduleName
    root == `Lean || root == `Init || root == `Nat || root == `String ||
      root == `Array || root == `List || root == `IO || root == `System

def isLeanCoreConstant (env : Environment) (name : Name) : Bool :=
  match getConstantModule env name with
  | none => false
  | some moduleName =>
    let root := moduleRoot moduleName
    root == `Lean || root == `Init || root == `Std || root == `Mathlib

def shouldSkipTrustedConstant (env : Environment) (name : Name) (trustModules : Array String) : Bool :=
  name == ``sorryAx ||
  isTrustedConstant env name trustModules ||
  isCoreModuleName env name ||
  isLeanCoreConstant env name

def isBuiltinInductive (name : Name) : Bool :=
  name == ``False || name == ``True || name == ``Empty || name == ``PEmpty

def hasSorry (e : Expr) : Bool :=
  foldExpr (fun acc expr => acc || match expr with
    | .const name _ => name == ``sorryAx
    | _ => false) false e

def isAxiom (info : ConstantInfo) : Bool :=
  match info with
  | .axiomInfo _ => true
  | _ => false

def collectDirectConstants (e : Expr) : NameSet :=
  foldExpr (fun acc expr => match expr with
    | .const name _ => acc.insert name
    | _ => acc) ∅ e

namespace Deps

structure Collector where
  seen  : Std.HashSet Name
  front : List Name
  back  : List Name
deriving Inhabited

namespace Collector

@[inline] def seed (visited : NameSet) (root : Name) : Collector :=
  let seeded := visited.toList.foldl (fun acc dep => acc.insert dep) Std.HashSet.emptyWithCapacity
  { seen := seeded.insert root, front := [root], back := [] }

@[inline] def dequeue? (state : Collector) : Option (Name × Collector) :=
  match state.front with
  | current :: rest => some (current, { state with front := rest })
  | [] =>
      match state.back.reverse with
      | [] => none
      | current :: rest =>
          some (current, { state with front := rest, back := [] })

@[inline] def enqueueIfNew (state : Collector) (skip : Name → Bool) (dep : Name) : Collector :=
  if state.seen.contains dep || skip dep then
    state
  else
    { seen := state.seen.insert dep, front := state.front, back := dep :: state.back }

@[inline] def enqueueAll (state : Collector) (skip : Name → Bool) (deps : List Name) : Collector :=
  deps.foldl (fun st dep => st.enqueueIfNew skip dep) state

end Collector

end Deps

/-- Collect all constants transitively used by a constant -/
partial def visitTransitiveDeps (env : Environment) (name : Name)
    (visitor : Name → ConstantInfo → IO (Option CheckFailure))
    (visited : NameSet := ∅) (trustModules : Array String := #[])
    (allowOpaqueBodies : Bool := true) : IO (Option CheckFailure × NameSet) := do
  let skip := shouldSkipConstant env trustModules
  if visited.contains name || skip name then
    return (none, visited)

  let mut state := Deps.Collector.seed visited name
  let mut visited := visited

  -- We use a loop with IO
  let rec loop (state : Deps.Collector) (visited : NameSet) : IO (Option CheckFailure × NameSet) := do
    match state.dequeue? with
    | none => return (none, visited)
    | some (current, pending) =>
        if visited.contains current || skip current then
          loop pending visited
        else
          let visited := visited.insert current
          match env.find? current with
          | none => loop pending visited
          | some info =>
              -- Run visitor
              if let some failure ← visitor current info then
                return (some failure, visited)

              let nextState :=
                match Lean.Compiler.implementedByAttr.getParam? env current with
                | some implName => pending.enqueueIfNew skip implName
                | none => pending

              let nextState :=
                match info.value? (allowOpaque := allowOpaqueBodies) with
                | some value => nextState.enqueueAll skip (collectDirectConstants value).toList
                | none => nextState

              let nextState := nextState.enqueueAll skip (collectDirectConstants info.type).toList
              loop nextState visited

  loop state visited

def findNativeComputationInDeps (deps : NameSet) (selfName : Name) : Option Name :=
  deps.toList.find? fun dep => dep != selfName && isNativeComputationName dep

def collectModulesToReplay (env : Environment) (allDeps : NameSet) (trustModules : Array String) : NameSet :=
  allDeps.foldl (init := ∅) fun modules depName =>
    if isTrustedConstant env depName trustModules then modules
    else match getConstantModule env depName with
      | some modName =>
        if isTrustedModuleName modName trustModules then modules
        else modules.insert modName
      | none => modules

structure CSimpCache where
  entries : Std.HashMap Name (Name × Lean.Compiler.CSimp.Entry)
  scannedModules : Std.HashSet Nat

def mkCSimpCache : CSimpCache := { entries := Std.HashMap.emptyWithCapacity, scannedModules := Std.HashSet.emptyWithCapacity }

def checkIsCSimp (env : Environment) (cache : IO.Ref CSimpCache) (name : Name) : IO (Option (Name × Lean.Compiler.CSimp.Entry)) := do
  let c ← cache.get
  if let some entry := c.entries.get? name then
    return some entry

  let some modIdx := env.getModuleIdxFor? name | return none
  let idx := modIdx.toNat
  if c.scannedModules.contains idx then
    return none

  -- Scan module
  let moduleName := env.allImportedModuleNames[idx]!
  let entries := Lean.Compiler.CSimp.ext.ext.getModuleEntries env modIdx
  let mut newEntries := c.entries
  for entry in entries do
    let data : Lean.Compiler.CSimp.Entry :=
      match entry with
      | ScopedEnvExtension.Entry.global data => data
      | ScopedEnvExtension.Entry.scoped _ data => data
    newEntries := newEntries.insert data.thmName (moduleName, data)

  cache.set { entries := newEntries, scannedModules := c.scannedModules.insert idx }

  return newEntries.get? name

def findSourceFile (_env : Environment) (moduleName : Name) : IO (Option System.FilePath) := do
  let relPath := System.FilePath.mk (moduleName.toString.replace "." "/") |>.addExtension "lean"
  let cwd ← IO.currentDir
  let searchPaths ← searchPathRef.get

  for base in cwd :: searchPaths do
    for path in [base / relPath, base / ".." / ".." / ".." / relPath] do
      if ← path.pathExists then return some path

  return none

/-- Cache for source file contents to avoid redundant disk I/O -/
abbrev SourceFileCache := Std.HashMap System.FilePath (Array String)

/-- Read a source file with caching to avoid redundant I/O -/
def readSourceFileCached (cache : IO.Ref SourceFileCache) (filePath : System.FilePath) : IO (Array String) := do
  let cached ← cache.get
  match cached.get? filePath with
  | some lines => return lines
  | none =>
      if !(← filePath.pathExists) then
        return #[]
      let content ← IO.FS.readFile filePath
      let lines := (content.splitOn "\n").toArray
      cache.modify (·.insert filePath lines)
      return lines

end LeanParanoia
