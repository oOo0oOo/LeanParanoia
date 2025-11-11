namespace LeanTestProject.AuxiliaryShadowing.TheoremShadowing

def bar (n : Nat) : Nat :=
  match n with
  | 0 => 0
  | n + 1 => n

theorem exploit : ∀ n, bar n = bar n := by
  sorry

end LeanTestProject.AuxiliaryShadowing.TheoremShadowing
