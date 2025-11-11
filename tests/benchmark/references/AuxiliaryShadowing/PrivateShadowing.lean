namespace LeanTestProject.AuxiliaryShadowing.PrivateShadowing

def bar : List Nat → Nat
  | [] => 0
  | x :: xs => x + bar xs

noncomputable def foo : List Nat → Nat
  | [] => 0
  | x :: xs => x + foo xs

theorem exploit : foo [1,2,3] = bar [1,2,3] := sorry

end LeanTestProject.AuxiliaryShadowing.PrivateShadowing
