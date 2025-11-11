namespace LeanTestProject.AuxiliaryShadowing.TypeSignature

def bar (n : Nat) : Nat :=
  match n with
  | 0 => 0
  | n + 1 => n

def exploit : (n : Nat) → bar n = bar n :=
  fun n => by sorry

end LeanTestProject.AuxiliaryShadowing.TypeSignature
