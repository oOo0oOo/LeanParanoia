namespace LeanTestProject.AuxiliaryShadowing.MatcherShadowing

def bar (n : Nat) : Nat :=
  match n with
  | 0 => 0
  | n + 1 => n

def foo : Nat → Nat
  | 0 => 0
  | n + 1 => n

theorem test1 : bar 5 = 4 := sorry
theorem test2 : foo 5 = 4 := sorry

end LeanTestProject.AuxiliaryShadowing.MatcherShadowing
