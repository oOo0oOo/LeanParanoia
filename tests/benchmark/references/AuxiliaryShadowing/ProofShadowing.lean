namespace LeanTestProject.AuxiliaryShadowing.ProofShadowing

def bar (n : Nat) : Nat :=
  match n with
  | 0 => 0
  | n + 1 => n

def foo (n : Nat) : Nat :=
  match n with
  | 0 => 0
  | k + 1 => k

theorem exploit : foo 5 = 4 := sorry

end LeanTestProject.AuxiliaryShadowing.ProofShadowing
