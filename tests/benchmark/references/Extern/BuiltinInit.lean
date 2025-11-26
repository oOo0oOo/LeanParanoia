-- Builtin init attribute creates foreign initialization hooks that run at startup
-- While this is a runtime security concern, it doesn't affect logical soundness
@[builtin_init]
def builtinInitHook : IO Unit := pure ()

theorem exploit_theorem : True := True.intro
