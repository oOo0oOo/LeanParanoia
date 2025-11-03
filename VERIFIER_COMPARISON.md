# Exploit Test Files

**Note**: Each tool is designed for different purposes and performing according to its specifications.

## Tool Comparison Results

| Exploit | LeanParanoia | lean4checker | SafeVerify |
|---------|--------------|--------------|------------|
| CSimp/WithAxiom | 🛑 1361ms (849ms)<br>CSimp; CustomAxioms | 🟢 2485ms | 🛑 1324ms<br>exploit_axiom is not in the allowed set of standard axioms |
| CSimp/WithUnsafe | 🛑 1322ms (834ms)<br>CSimp; CustomAxioms | 🟢 2444ms | 🛑 1341ms<br>exploit_axiom is not in the allowed set of standard axioms |
| ConstructorIntegrity/ManualConstructor | 🛑 1200ms (818ms)<br>ConstructorIntegrity; CustomAxioms; RecursorIntegrity | 🟢 2485ms | 🟡 1335ms<br>definition exploit_theorem does not match the requirement |
| CustomAxioms/FakeStdLib | 🛑 3216ms (1217ms)<br>CustomAxioms | 🟢 2883ms | 🛑 1732ms<br>Std.TrustMe.forgedFalse is not in the allowed set of standard axioms |
| CustomAxioms/ForgeRunCmd | 🛑 3170ms (1239ms)<br>CustomAxioms | 🟢 2862ms | 🛑 1737ms<br>RunCmdForgedFalse is not in the allowed set of standard axioms |
| CustomAxioms/ForgeRunTac | 🛑 3206ms (1210ms)<br>CustomAxioms | 🟢 2909ms | 🛑 1701ms<br>RunTacForgedFalse is not in the allowed set of standard axioms |
| CustomAxioms/HiddenInInstance | 🛑 1326ms (842ms)<br>CustomAxioms | 🟢 2478ms | 🛑 1312ms<br>LeanTestProject.CustomAxioms.HiddenInInstance.hidden_axiom is not in the allowed set of standard axioms |
| CustomAxioms/HiddenInMacro | 🛑 1332ms (781ms)<br>CustomAxioms | 🟢 2395ms | 🛑 1309ms<br>LeanTestProject.CustomAxioms.HiddenInMacro.hidden_axiom is not in the allowed set of standard axioms |
| CustomAxioms/ProveAnything | 🛑 1300ms (802ms)<br>CustomAxioms | 🟢 2443ms | 🛑 1261ms<br>magic is not in the allowed set of standard axioms |
| CustomAxioms/ProveFalse | 🛑 1289ms (793ms)<br>CustomAxioms | 🟢 2390ms | 🛑 1301ms<br>exploit_axiom is not in the allowed set of standard axioms |
| CustomAxioms/SkipKernelTC | 🛑 1328ms (796ms)<br>CustomAxioms | 🟢 2411ms | 🟢 1264ms |
| Extern/BuiltinInit | 🛑 1585ms (789ms)<br>Extern | 🟢 2397ms | 🟢 1273ms |
| Extern/CoreNamespace | 🛑 1294ms (792ms)<br>CustomAxioms; Extern | 🟢 2467ms | 🟡 1299ms<br>error during verification |
| Extern/ExportC | 🛑 1330ms (792ms)<br>CustomAxioms; Extern | 🟢 2414ms | 🛑 1291ms<br>exploit_axiom is not in the allowed set of standard axioms |
| Extern/ExternFFI | 🛑 1312ms (790ms)<br>CustomAxioms; Extern | 🟢 2443ms | 🛑 1264ms<br>exploit_axiom is not in the allowed set of standard axioms |
| Extern/InitHook | 🛑 1500ms (785ms)<br>Extern | 🟢 2387ms | 🟢 1285ms |
| Extern/PrivateExtern | 🛑 1296ms (781ms)<br>CustomAxioms; Extern | 🟢 2463ms | 🛑 1278ms<br>exploit_axiom is not in the allowed set of standard axioms |
| ImplementedBy/ChainedReplacement | 🛑 1304ms (784ms)<br>CustomAxioms; Extern; ImplementedBy | 🟢 2473ms | 🛑 1278ms<br>exploit_axiom is not in the allowed set of standard axioms |
| ImplementedBy/DirectReplacement | 🛑 1292ms (784ms)<br>CustomAxioms; ImplementedBy | 🟢 2409ms | 🛑 1258ms<br>exploit_axiom is not in the allowed set of standard axioms |
| ImplementedBy/PrivateImpl | 🛑 1286ms (800ms)<br>CustomAxioms; ImplementedBy | 🟢 2439ms | 🛑 1302ms<br>exploit_axiom is not in the allowed set of standard axioms |
| KernelRejection/NonPositive | 🛑 663ms (672ms)<br>KernelRejection | 🛑 2283ms<br>Could not find any oleans for: LeanTestProject.KernelRejection.NonPositive | 🟡 N/A<br>error during verification |
| KernelRejection/UnsafeCast | 🛑 653ms (662ms)<br>KernelRejection | 🛑 2319ms<br>Could not find any oleans for: LeanTestProject.KernelRejection.UnsafeCast | 🟡 N/A<br>error during verification |
| Metavariables/Timeout | 🛑 1354ms (809ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2441ms | 🟡 1283ms<br>theorem exploit_theorem does not have the same type as the requirement |
| Metavariables/TypeclassFail | 🛑 1320ms (795ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2404ms | 🟡 1266ms<br>theorem exploit_theorem does not have the same type as the requirement |
| NativeComputation/NativeDecide | 🛑 1419ms (806ms)<br>CustomAxioms; NativeComputation; Replay | 🛑 2386ms<br>(kernel) (interpreter) unknown declaration 'exploit_theorem._nativeDecide_1_1' | 🛑 1280ms<br>(kernel) (interpreter) unknown declaration 'exploit_theorem._nativeDecide_1_1' |
| NativeComputation/OfReduce | 🛑 1745ms (921ms)<br>CustomAxioms; NativeComputation; Replay | 🛑 2535ms<br>(kernel) (interpreter) unknown declaration 'exploit_theorem._nativeDecide_1_1' | 🛑 1388ms<br>(kernel) (interpreter) unknown declaration 'exploit_theorem._nativeDecide_1_1' |
| Partial/NonTerminating | 🛑 1316ms (778ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2437ms | 🟡 N/A<br>error during verification |
| RecursorIntegrity/MissingRecursor | 🛑 1187ms (784ms)<br>ConstructorIntegrity; CustomAxioms; RecursorIntegrity | 🟢 2404ms | 🟡 1258ms<br>definition exploit_theorem does not match the requirement |
| Sorry/Admit | 🛑 1306ms (784ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2422ms | 🛑 1259ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/ByAsSorry | 🛑 1341ms (796ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2430ms | 🛑 1273ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/Direct | 🛑 1294ms (785ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2404ms | 🛑 1252ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/Intermediate | 🛑 1380ms (777ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2418ms | 🛑 1281ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/Opaque | 🛑 3076ms (1210ms)<br>CustomAxioms; Sorry | 🟢 2829ms | 🛑 1647ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/ProofAsSorry | 🛑 1283ms (786ms)<br>CustomAxioms; Sorry | 🟢 2403ms | 🛑 1270ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/TerminalTactics | 🛑 1338ms (784ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2407ms | 🛑 1266ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/Underscore | 🛑 1307ms (790ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2429ms | 🛑 1279ms<br>sorryAx is not in the allowed set of standard axioms |
| SourcePatterns/LocalInstance | 🛑 1330ms (788ms)<br>SourcePatterns | 🟢 2392ms | 🟡 1274ms<br>sorryAx detected in proof |
| SourcePatterns/LocalInstanceArithmetic | 🛑 1284ms (802ms)<br>SourcePatterns | 🟢 2449ms | 🟡 1269ms<br>theorem exploit_theorem does not have the same type as the requirement |
| SourcePatterns/LocalMacroRules | 🛑 1289ms (784ms)<br>CustomAxioms; SourcePatterns | 🟢 2410ms | 🛑 1278ms<br>LeanTestProject.SourcePatterns.LocalMacroRules.hidden_axiom is not in the allowed set of standard axioms |
| SourcePatterns/LocalNotation | 🛑 1275ms (796ms)<br>SourcePatterns | 🟢 2432ms | 🟡 1268ms<br>error during verification |
| SourcePatterns/NotationRedefinition | 🛑 1286ms (793ms)<br>CustomAxioms; SourcePatterns | 🟢 2455ms | 🟡 1272ms<br>sorryAx detected in proof |
| SourcePatterns/ScopedNotation | 🛑 1276ms (777ms)<br>CustomAxioms; SourcePatterns | 🟢 2391ms | 🟡 N/A<br>error during verification |
| Transitive/DeepAxiom_L1 | 🛑 1640ms (789ms)<br>CustomAxioms | 🟢 2377ms | 🛑 1302ms<br>custom_axiom is not in the allowed set of standard axioms |
| Transitive/DeepSorry_L1 | 🛑 1665ms (795ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2394ms | 🛑 1271ms<br>sorryAx is not in the allowed set of standard axioms |
| Transitive/DeepSorry_L2 | 🛑 2022ms (788ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2415ms | 🛑 1261ms<br>sorryAx is not in the allowed set of standard axioms |
| Transitive/Level2_UsesBoth | 🟢 1655ms (1677ms) | 🟢 2432ms | 🟡 1266ms<br>theorem uses_both does not have the same type as the requirement |
| Transitive/UsesBadLib | 🛑 1595ms (780ms)<br>CustomAxioms | 🟢 2426ms | 🛑 1249ms<br>BadLib.hiddenAssumption is not in the allowed set of standard axioms |
| Unsafe/UnsafeDefinition | 🛑 1284ms (788ms)<br>CustomAxioms; ImplementedBy; Unsafe | 🟢 2395ms | 🛑 1274ms<br>exploit_axiom is not in the allowed set of standard axioms |
| Valid/Dependencies | 🟢 1656ms (1651ms) | 🟢 2409ms | 🟡 1267ms<br>theorem uses_helper does not have the same type as the requirement |
| Valid/Helper | 🟢 1275ms (1299ms) | 🟢 2407ms | 🟡 1262ms<br>theorem helper_theorem does not have the same type as the requirement |
| Valid/Simple | 🟢 1353ms (1409ms) | 🟢 2437ms | 🟢 1264ms |
| Valid/UnsafeReducibility | 🟢 1309ms (1298ms) | 🟢 2418ms | 🟡 N/A<br>error during verification |
| Valid/WithAxioms | 🟢 1442ms (1419ms) | 🟢 2415ms | 🟢 1269ms<br>sorryAx detected in proof |

---

### Legend

- 🛑 **Detected**: Tool identified an exploit
- 🟢 **Passed**: Tool did not detect any exploit
- 🟡 **N/A**: Test setup issue or methodology limitation

**Time Format**: For LeanParanoia: `full_time (fail-fast_time)`

Note: WIP, might contain inaccuracies.