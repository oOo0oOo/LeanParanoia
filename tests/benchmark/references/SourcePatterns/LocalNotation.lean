namespace LeanTestProject.SourcePatterns.LocalNotation

-- No local notation - use actual type to test if SafeVerify catches the mismatch
notation a " ≈ " b => a - b = 2

theorem exploit_theorem : (5 : Nat) ≈ 3 := sorry

end LeanTestProject.SourcePatterns.LocalNotation
