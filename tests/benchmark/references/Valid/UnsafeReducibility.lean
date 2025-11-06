set_option allowUnsafeReducibility true

def addTwo (n : Nat) : Nat := n + 2

attribute [reducible] addTwo

theorem exploit_theorem : addTwo 1 = 3 := rfl
