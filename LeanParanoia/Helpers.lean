import Lean
import Lean.Compiler.CSimpAttr
import LeanParanoia.Types
import LeanParanoia.Config

open Lean Meta Elab Std

namespace LeanParanoia

def getConstantModule (env : Environment) (name : Name) : Option Name :=
  env.getModuleIdxFor? name >>= fun idx => env.allImportedModuleNames[idx.toNat]?

def matchesTrustedPrefix (moduleStr : String) (trustModules : Array String) : Bool :=
  trustModules.any fun pref =>
    moduleStr == pref || (moduleStr.startsWith pref && moduleStr.get! ⟨pref.length⟩ == '.')

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
partial def collectTransitiveDeps (env : Environment) (name : Name)
    (visited : NameSet := ∅) (trustModules : Array String := #[])
    (allowOpaqueBodies : Bool := true) : NameSet :=
  let skip := shouldSkipConstant env trustModules
  if visited.contains name || skip name then
    visited
  else
    let rec loop (state : Deps.Collector) (acc : NameSet) : NameSet :=
      match state.dequeue? with
      | none => acc
      | some (current, pending) =>
          if acc.contains current || skip current then
            loop pending acc
          else
            let acc := acc.insert current
            let nextState :=
              match env.find? current with
              | none => pending
              | some info =>
                  let afterImpl :=
                    match Lean.Compiler.implementedByAttr.getParam? env current with
                    | some implName => pending.enqueueIfNew skip implName
                    | none => pending
                  let afterValue :=
                    match info.value? (allowOpaque := allowOpaqueBodies) with
                    | some value => afterImpl.enqueueAll skip (collectDirectConstants value).toList
                    | none => afterImpl
                  afterValue.enqueueAll skip (collectDirectConstants info.type).toList
            loop nextState acc
    loop (Deps.Collector.seed visited name) visited

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

abbrev CSimpEntryMap := Std.HashMap Name (Name × Lean.Compiler.CSimp.Entry)

def buildCSimpEntryMap (env : Environment) : CSimpEntryMap :=
  let moduleNames := env.allImportedModuleNames
  let totalSize := moduleNames.size
  let initialCapacity := totalSize * 4
  let rec loop (idx : Nat) (acc : CSimpEntryMap) : CSimpEntryMap :=
    if h : idx < totalSize then
      let moduleName := moduleNames[idx]!
      let entries := Lean.Compiler.CSimp.ext.ext.getModuleEntries env idx
      let acc := entries.foldl (init := acc) fun acc entry =>
        let data : Lean.Compiler.CSimp.Entry :=
          match entry with
          | ScopedEnvExtension.Entry.global data => data
          | ScopedEnvExtension.Entry.scoped _ data => data
        acc.insert data.thmName (moduleName, data)
      loop (idx + 1) acc
    else
      acc
  loop 0 (Std.HashMap.emptyWithCapacity initialCapacity)

def csimpEntry? (csimpMap : CSimpEntryMap) (name : Name) : Option (Name × Lean.Compiler.CSimp.Entry) :=
  csimpMap.get? name

def findSourceFile (_env : Environment) (moduleName : Name) : IO (Option System.FilePath) := do
  let relPath := System.FilePath.mk (moduleName.toString.replace "." "/") |>.addExtension "lean"
  let cwd ← IO.currentDir
  let searchPaths ← searchPathRef.get

  for base in cwd :: searchPaths do
    for path in [base / relPath, base / ".." / ".." / ".." / relPath] do
      if ← path.pathExists then return some path

  return none

end LeanParanoia
