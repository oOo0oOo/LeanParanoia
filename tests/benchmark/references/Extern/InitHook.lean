-- Init attribute creates foreign initialization hooks that run at module load
-- While this is a runtime security concern, it doesn't affect logical soundness
@[init]
def initHook : IO Unit := pure ()

theorem exploit_theorem : True := True.intro
