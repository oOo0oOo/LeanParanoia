namespace LeanTestProject.Partial.NonTerminating

partial def loop (n : Nat) : Nat := loop (n + 1)

theorem exploit_theorem : loop 0 = 42 := sorry

end LeanTestProject.Partial.NonTerminating
