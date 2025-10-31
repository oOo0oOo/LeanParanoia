import Lean.Data.Json

open Lean Std

abbrev FailureMap := List (String × List String)

namespace FailureMap

@[inline] def empty : FailureMap := []

@[inline] def insert (m : FailureMap) (check : String) (message : String) : FailureMap :=
  let rec loop (revPrefix : List (String × List String)) (rest : List (String × List String)) : FailureMap :=
    match rest with
    | [] => revPrefix.reverse ++ [(check, [message])]
    | (name, messages) :: tail =>
        if name == check then
          revPrefix.reverse ++ (name, messages ++ [message]) :: tail
        else
          loop ((name, messages) :: revPrefix) tail
  loop [] m

def toJson (m : FailureMap) : Json :=
  let entries := m.map fun (check, messages) =>
    let payload := Json.arr ((messages.map Json.str).toArray)
    (check, payload)
  Json.mkObj entries

end FailureMap

inductive TestResult where
  | Pass : TestResult
  | Fail (reason : String) : TestResult
deriving Repr, BEq

def TestResult.isPass : TestResult → Bool
  | TestResult.Pass => true
  | TestResult.Fail _ => false

structure NamedTest where
  name : String
  result : TestResult
deriving Repr

structure VerificationResult where
  success : Bool
  failures : FailureMap
  errorTrace : Option String := none
deriving Repr

def VerificationResult.fromTests (tests : List NamedTest) : VerificationResult :=
  let failures := tests.foldl (init := FailureMap.empty) fun acc test =>
    match test.result with
    | TestResult.Pass => acc
    | TestResult.Fail reason => FailureMap.insert acc test.name s!"{test.name}: {reason}"
  { success := failures.isEmpty
  , failures := failures }

instance : ToJson VerificationResult where
  toJson
    | { success, failures, errorTrace } =>
        let base :=
          [ ("success", Json.bool success)
          , ("failures", FailureMap.toJson failures) ]
        let fields :=
          match errorTrace with
          | some trace => base ++ [("errorTrace", Json.str trace)]
          | none => base
        Json.mkObj fields
