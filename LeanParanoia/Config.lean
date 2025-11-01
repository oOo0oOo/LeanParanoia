structure VerificationConfig where
  checkSorry : Bool := true
  checkMetavariables : Bool := true
  checkUnsafe : Bool := true
  checkPartial : Bool := true
  checkAxioms : Bool := true
  checkConstructors : Bool := true
  checkRecursors : Bool := true
  checkExtern : Bool := true
  checkImplementedBy : Bool := true
  checkCSimp : Bool := true
  checkNativeComputation : Bool := true
  checkOpaqueBodies : Bool := true
  checkSource : Bool := true
  enableReplay : Bool := true
  failFast : Bool := false
  allowedAxioms : List String := ["propext", "Quot.sound", "Classical.choice"]
  sourceBlacklist : List String := [
    "local instance",
    "local notation",
    "local macro_rules",
    "local syntax",
    "local infix",
    "local infixl",
    "local infixr",
    "local prefix",
    "local postfix",
    "scoped instance",
    "scoped notation"
  ]
  sourceWhitelist : List String := []
  trustModules : Array String := #[]
deriving Repr

def VerificationConfig.default : VerificationConfig := {}
