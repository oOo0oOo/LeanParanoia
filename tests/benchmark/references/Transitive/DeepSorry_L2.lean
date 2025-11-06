import LeanTestProject.Transitive.DeepSorry_L1

theorem uses_sorry_transitively : True := by
  have : True := uses_sorry_from_l0
  exact this
