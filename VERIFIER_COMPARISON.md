# Exploit Test Files

**Note**: Each tool is designed for different purposes and performing according to its specifications.

## Tool Comparison Results

| Exploit | LeanParanoia | lean4checker | SafeVerify |
|---------|--------------|--------------|------------|
| AuxiliaryShadowing/MatcherShadowing [↗](tests/lean_exploit_files/AuxiliaryShadowing/MatcherShadowing.lean) | 🟢 1465ms (1482ms) | 🟢 2596ms | 🛑 1461ms<br>definition LeanTestProject.AuxiliaryShadowing.MatcherShadowing.foo does not m... |
| AuxiliaryShadowing/PrivateShadowing [↗](tests/lean_exploit_files/AuxiliaryShadowing/PrivateShadowing.lean) | 🟢 1484ms (1501ms) | 🟢 2577ms | 🛑 1478ms<br>definition LeanTestProject.AuxiliaryShadowing.PrivateShadowing.foo does not m... |
| AuxiliaryShadowing/ProofShadowing [↗](tests/lean_exploit_files/AuxiliaryShadowing/ProofShadowing.lean) | 🟢 1510ms (1593ms) | 🟢 2647ms | 🛑 1461ms<br>definition LeanTestProject.AuxiliaryShadowing.ProofShadowing.foo does not mat... |
| AuxiliaryShadowing/TheoremShadowing [↗](tests/lean_exploit_files/AuxiliaryShadowing/TheoremShadowing.lean) | 🛑 1526ms (1514ms)<br>Replay | 🟢 2587ms | 🛑 1489ms<br>theorem LeanTestProject.AuxiliaryShadowing.TheoremShadowing.exploit does not ... |
| AuxiliaryShadowing/TypeSignature [↗](tests/lean_exploit_files/AuxiliaryShadowing/TypeSignature.lean) | 🛑 1551ms (1521ms)<br>Replay | 🟢 2585ms | 🛑 1487ms<br>definition LeanTestProject.AuxiliaryShadowing.TypeSignature.exploit does not ... |
| CSimp/WithAxiom [↗](tests/lean_exploit_files/CSimp/WithAxiom.lean) | 🛑 1564ms (1022ms)<br>CSimp; CustomAxioms | 🟢 2703ms | 🛑 1535ms<br>exploit_axiom is not in the allowed set of standard axioms |
| CSimp/WithUnsafe [↗](tests/lean_exploit_files/CSimp/WithUnsafe.lean) | 🛑 1542ms (1049ms)<br>CSimp; CustomAxioms | 🟢 2731ms | 🛑 1537ms<br>exploit_axiom is not in the allowed set of standard axioms |
| ConstructorIntegrity/ManualConstructor [↗](tests/lean_exploit_files/ConstructorIntegrity/ManualConstructor.lean) | 🛑 1423ms (1056ms)<br>ConstructorIntegrity; CustomAxioms; RecursorIntegrity | 🟢 2694ms | 🛑 1554ms<br>definition exploit_theorem does not match the requirement |
| CustomAxioms/FakeStdLib [↗](tests/lean_exploit_files/CustomAxioms/FakeStdLib.lean) | 🛑 3512ms (1448ms)<br>CustomAxioms | 🟢 3101ms | 🛑 1940ms<br>Std.TrustMe.forgedFalse is not in the allowed set of standard axioms |
| CustomAxioms/ForgeRunCmd [↗](tests/lean_exploit_files/CustomAxioms/ForgeRunCmd.lean) | 🛑 3449ms (1435ms)<br>CustomAxioms | 🟢 3177ms | 🛑 1922ms<br>RunCmdForgedFalse is not in the allowed set of standard axioms |
| CustomAxioms/ForgeRunTac [↗](tests/lean_exploit_files/CustomAxioms/ForgeRunTac.lean) | 🛑 3442ms (1413ms)<br>CustomAxioms | 🟢 3115ms | 🛑 1939ms<br>RunTacForgedFalse is not in the allowed set of standard axioms |
| CustomAxioms/HiddenInInstance [↗](tests/lean_exploit_files/CustomAxioms/HiddenInInstance.lean) | 🛑 1601ms (996ms)<br>CustomAxioms | 🟢 2712ms | 🛑 1563ms<br>LeanTestProject.CustomAxioms.HiddenInInstance.hidden_axiom is not in the allowed set of standard axioms |
| CustomAxioms/HiddenInMacro [↗](tests/lean_exploit_files/CustomAxioms/HiddenInMacro.lean) | 🛑 1577ms (1048ms)<br>CustomAxioms | 🟢 2719ms | 🛑 1513ms<br>LeanTestProject.CustomAxioms.HiddenInMacro.hidden_axiom is not in the allowed set of standard axioms |
| CustomAxioms/ProveAnything [↗](tests/lean_exploit_files/CustomAxioms/ProveAnything.lean) | 🛑 1532ms (1037ms)<br>CustomAxioms | 🟢 2774ms | 🛑 1556ms<br>magic is not in the allowed set of standard axioms |
| CustomAxioms/ProveFalse [↗](tests/lean_exploit_files/CustomAxioms/ProveFalse.lean) | 🛑 1554ms (1041ms)<br>CustomAxioms | 🟢 2707ms | 🛑 1548ms<br>exploit_axiom is not in the allowed set of standard axioms |
| CustomAxioms/SkipKernelTC [↗](tests/lean_exploit_files/CustomAxioms/SkipKernelTC.lean) | 🛑 1552ms (1018ms)<br>CustomAxioms | 🟢 2712ms | 🟢 1549ms |
| Extern/BuiltinInit [↗](tests/lean_exploit_files/Extern/BuiltinInit.lean) | 🛑 1853ms (1022ms)<br>Extern | 🟢 2665ms | 🟢 1520ms |
| Extern/CoreNamespace [↗](tests/lean_exploit_files/Extern/CoreNamespace.lean) | 🛑 1540ms (1040ms)<br>CustomAxioms; Extern | 🟢 2699ms | 🛑 1531ms<br>exploit_axiom is not in the allowed set of standard axioms |
| Extern/ExportC [↗](tests/lean_exploit_files/Extern/ExportC.lean) | 🛑 1632ms (1027ms)<br>CustomAxioms; Extern | 🟢 2732ms | 🛑 1564ms<br>exploit_axiom is not in the allowed set of standard axioms |
| Extern/ExternFFI [↗](tests/lean_exploit_files/Extern/ExternFFI.lean) | 🛑 1543ms (1033ms)<br>CustomAxioms; Extern | 🟢 2746ms | 🛑 1539ms<br>exploit_axiom is not in the allowed set of standard axioms |
| Extern/InitHook [↗](tests/lean_exploit_files/Extern/InitHook.lean) | 🛑 1790ms (1011ms)<br>Extern | 🟢 2706ms | 🟢 1558ms |
| Extern/PrivateExtern [↗](tests/lean_exploit_files/Extern/PrivateExtern.lean) | 🛑 1594ms (1013ms)<br>CustomAxioms; Extern | 🟢 2741ms | 🛑 1552ms<br>exploit_axiom is not in the allowed set of standard axioms |
| ImplementedBy/ChainedReplacement [↗](tests/lean_exploit_files/ImplementedBy/ChainedReplacement.lean) | 🛑 1547ms (1033ms)<br>CustomAxioms; Extern; ImplementedBy | 🟢 2685ms | 🛑 1538ms<br>exploit_axiom is not in the allowed set of standard axioms |
| ImplementedBy/DirectReplacement [↗](tests/lean_exploit_files/ImplementedBy/DirectReplacement.lean) | 🛑 1605ms (1097ms)<br>CustomAxioms; ImplementedBy; Unsafe | 🟢 2738ms | 🛑 1536ms<br>exploit_axiom is not in the allowed set of standard axioms |
| ImplementedBy/PrivateImpl [↗](tests/lean_exploit_files/ImplementedBy/PrivateImpl.lean) | 🛑 1603ms (1056ms)<br>CustomAxioms; ImplementedBy; Unsafe | 🟢 2724ms | 🛑 1520ms<br>exploit_axiom is not in the allowed set of standard axioms |
| KernelRejection/NonPositive [↗](tests/lean_exploit_files/KernelRejection/NonPositive.lean) | 🛑 894ms (893ms)<br>KernelRejection | 🛑 2567ms<br>Could not find any oleans for: LeanTestProject.KernelRejection.NonPositive | 🟡 N/A<br>error during verification |
| KernelRejection/UnsafeCast [↗](tests/lean_exploit_files/KernelRejection/UnsafeCast.lean) | 🛑 917ms (929ms)<br>KernelRejection | 🛑 2619ms<br>Could not find any oleans for: LeanTestProject.KernelRejection.UnsafeCast | 🟡 N/A<br>error during verification |
| Metavariables/Timeout [↗](tests/lean_exploit_files/Metavariables/Timeout.lean) | 🛑 1569ms (1024ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2759ms | 🛑 1574ms<br>sorryAx is not in the allowed set of standard axioms |
| Metavariables/TypeclassFail [↗](tests/lean_exploit_files/Metavariables/TypeclassFail.lean) | 🛑 1586ms (1037ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2714ms | 🛑 1541ms<br>sorryAx is not in the allowed set of standard axioms |
| NativeComputation/NativeDecide [↗](tests/lean_exploit_files/NativeComputation/NativeDecide.lean) | 🛑 1672ms (1036ms)<br>CustomAxioms; NativeComputation; Replay | 🛑 2682ms<br>(kernel) (interpreter) unknown declaration 'exploit_theorem._nativeDecide_1_1' | 🛑 1551ms<br>(kernel) (interpreter) unknown declaration 'exploit_theorem._nativeDecide_1_1' |
| NativeComputation/OfReduce [↗](tests/lean_exploit_files/NativeComputation/OfReduce.lean) | 🛑 2048ms (1166ms)<br>CustomAxioms; NativeComputation; Replay | 🛑 2854ms<br>(kernel) (interpreter) unknown declaration 'exploit_theorem._nativeDecide_1_1' | 🛑 1674ms<br>(kernel) (interpreter) unknown declaration 'exploit_theorem._nativeDecide_1_1' |
| Partial/NonTerminating [↗](tests/lean_exploit_files/Partial/NonTerminating.lean) | 🛑 1575ms (1037ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2710ms | 🛑 1591ms<br>sorryAx is not in the allowed set of standard axioms |
| RecursorIntegrity/MissingRecursor [↗](tests/lean_exploit_files/RecursorIntegrity/MissingRecursor.lean) | 🛑 1439ms (1014ms)<br>ConstructorIntegrity; CustomAxioms; RecursorIntegrity | 🟢 2773ms | 🛑 1573ms<br>definition exploit_theorem does not match the requirement |
| Sorry/Admit [↗](tests/lean_exploit_files/Sorry/Admit.lean) | 🛑 1574ms (1026ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2698ms | 🛑 1532ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/ByAsSorry [↗](tests/lean_exploit_files/Sorry/ByAsSorry.lean) | 🛑 1563ms (1024ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2691ms | 🛑 1534ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/Direct [↗](tests/lean_exploit_files/Sorry/Direct.lean) | 🛑 1558ms (1038ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2713ms | 🛑 1542ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/Intermediate [↗](tests/lean_exploit_files/Sorry/Intermediate.lean) | 🛑 1657ms (1050ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2747ms | 🛑 1571ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/Opaque [↗](tests/lean_exploit_files/Sorry/Opaque.lean) | 🛑 3491ms (1446ms)<br>CustomAxioms; Sorry | 🟢 3109ms | 🛑 1938ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/ProofAsSorry [↗](tests/lean_exploit_files/Sorry/ProofAsSorry.lean) | 🛑 1538ms (1015ms)<br>CustomAxioms; Sorry | 🟢 2687ms | 🛑 1502ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/TerminalTactics [↗](tests/lean_exploit_files/Sorry/TerminalTactics.lean) | 🛑 1631ms (1023ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2700ms | 🛑 1537ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/Underscore [↗](tests/lean_exploit_files/Sorry/Underscore.lean) | 🛑 1548ms (1010ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2706ms | 🛑 1528ms<br>sorryAx is not in the allowed set of standard axioms |
| SourcePatterns/LocalInstance [↗](tests/lean_exploit_files/SourcePatterns/LocalInstance.lean) | 🛑 1577ms (1006ms)<br>SourcePatterns | 🟢 2681ms | 🛑 1568ms<br>theorem LeanTestProject.SourcePatterns.LocalInstance.exploit_theorem does not... |
| SourcePatterns/LocalInstanceArithmetic [↗](tests/lean_exploit_files/SourcePatterns/LocalInstanceArithmetic.lean) | 🛑 1566ms (1021ms)<br>SourcePatterns | 🟢 2699ms | 🛑 1566ms<br>theorem exploit_theorem does not have the same type as the requirement |
| SourcePatterns/LocalMacroRules [↗](tests/lean_exploit_files/SourcePatterns/LocalMacroRules.lean) | 🛑 1575ms (1027ms)<br>CustomAxioms; SourcePatterns | 🟢 2731ms | 🛑 1564ms<br>LeanTestProject.SourcePatterns.LocalMacroRules.hidden_axiom is not in the allowed set of standard axioms |
| SourcePatterns/LocalNotation [↗](tests/lean_exploit_files/SourcePatterns/LocalNotation.lean) | 🛑 1586ms (1070ms)<br>SourcePatterns | 🟢 2711ms | 🛑 1610ms<br>exploit detected |
| SourcePatterns/NotationRedefinition [↗](tests/lean_exploit_files/SourcePatterns/NotationRedefinition.lean) | 🛑 1592ms (1042ms)<br>CustomAxioms; SourcePatterns | 🟢 2706ms | 🛑 1592ms<br>theorem LeanTestProject.SourcePatterns.NotationRedefinition.exploit_theorem d... |
| SourcePatterns/ScopedNotation [↗](tests/lean_exploit_files/SourcePatterns/ScopedNotation.lean) | 🛑 1626ms (1086ms)<br>CustomAxioms; SourcePatterns | 🟢 2715ms | 🛑 1568ms<br>exploit detected |
| Transitive/DeepAxiom_L1 [↗](tests/lean_exploit_files/Transitive/DeepAxiom_L1.lean) | 🛑 1999ms (1036ms)<br>CustomAxioms | 🟢 2702ms | 🛑 1556ms<br>custom_axiom is not in the allowed set of standard axioms |
| Transitive/DeepSorry_L1 [↗](tests/lean_exploit_files/Transitive/DeepSorry_L1.lean) | 🛑 1945ms (1006ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2695ms | 🛑 1544ms<br>sorryAx is not in the allowed set of standard axioms |
| Transitive/DeepSorry_L2 [↗](tests/lean_exploit_files/Transitive/DeepSorry_L2.lean) | 🛑 2367ms (1007ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2707ms | 🛑 1544ms<br>sorryAx is not in the allowed set of standard axioms |
| Transitive/Level2_UsesBoth [↗](tests/lean_exploit_files/Transitive/Level2_UsesBoth.lean) | 🟢 1971ms (1945ms) | 🟢 2692ms | 🟢 1537ms |
| Transitive/UsesBadLib [↗](tests/lean_exploit_files/Transitive/UsesBadLib.lean) | 🛑 1870ms (1011ms)<br>CustomAxioms | 🟢 2747ms | 🛑 1557ms<br>BadLib.hiddenAssumption is not in the allowed set of standard axioms |
| Unsafe/UnsafeDefinition [↗](tests/lean_exploit_files/Unsafe/UnsafeDefinition.lean) | 🛑 1648ms (1047ms)<br>CustomAxioms; ImplementedBy; Unsafe | 🟢 2715ms | 🛑 1561ms<br>exploit_axiom is not in the allowed set of standard axioms |
| Valid/ComplexExample [↗](tests/lean_exploit_files/Valid/ComplexExample.lean) | 🟢 1714ms (1721ms) | 🟢 2685ms | 🟡 N/A<br>error during verification |
| Valid/Dependencies [↗](tests/lean_exploit_files/Valid/Dependencies.lean) | 🟢 2033ms (1970ms) | 🟢 2765ms | 🟢 1590ms |
| Valid/Helper [↗](tests/lean_exploit_files/Valid/Helper.lean) | 🟢 1593ms (1537ms) | 🟢 2749ms | 🟢 1538ms |
| Valid/Simple [↗](tests/lean_exploit_files/Valid/Simple.lean) | 🟢 1597ms (1631ms) | 🟢 2709ms | 🟢 1527ms |
| Valid/UnsafeReducibility [↗](tests/lean_exploit_files/Valid/UnsafeReducibility.lean) | 🟢 1548ms (1529ms) | 🟢 2708ms | 🟢 1532ms |
| Valid/WithAxioms [↗](tests/lean_exploit_files/Valid/WithAxioms.lean) | 🟢 1683ms (1681ms) | 🟢 2651ms | 🟢 1553ms |

---

### Legend

- 🛑 **Detected**: Tool identified an exploit
- 🟢 **Passed**: Tool did not detect any exploit
- 🟡 **N/A**: Test setup issue or methodology limitation

**Time Format**: For LeanParanoia: `full_time (fail-fast_time)`

Note: WIP, might contain inaccuracies.