# Exploit Test Files

**Note**: Each tool is designed for different purposes and performing according to its specifications.

## Tool Comparison Results

| Exploit | LeanParanoia | lean4checker | SafeVerify |
|---------|--------------|--------------|------------|
| CSimp/WithAxiom | 🛑 1350ms (810ms)<br>CSimp; CustomAxioms | 🟢 2533ms | 🛑 1296ms<br>exploit_axiom is not in the allowed set of standard axioms |
| CSimp/WithUnsafe | 🛑 1344ms (827ms)<br>CSimp; CustomAxioms | 🟢 2470ms | 🛑 1311ms<br>exploit_axiom is not in the allowed set of standard axioms |
| ConstructorIntegrity/ManualConstructor | 🛑 1256ms (807ms)<br>ConstructorIntegrity; CustomAxioms; RecursorIntegrity | 🟢 2506ms | 🛑 1344ms<br>definition exploit_theorem does not match the requirement |
| CustomAxioms/FakeStdLib | 🛑 3195ms (1229ms)<br>CustomAxioms | 🟢 2910ms | 🛑 1690ms<br>Std.TrustMe.forgedFalse is not in the allowed set of standard axioms |
| CustomAxioms/ForgeRunCmd | 🛑 3263ms (1217ms)<br>CustomAxioms | 🟢 2925ms | 🛑 1724ms<br>RunCmdForgedFalse is not in the allowed set of standard axioms |
| CustomAxioms/ForgeRunTac | 🛑 3236ms (1271ms)<br>CustomAxioms | 🟢 2881ms | 🛑 1649ms<br>RunTacForgedFalse is not in the allowed set of standard axioms |
| CustomAxioms/HiddenInInstance | 🛑 1313ms (837ms)<br>CustomAxioms | 🟢 2480ms | 🛑 1285ms<br>LeanTestProject.CustomAxioms.HiddenInInstance.hidden_axiom is not in the allowed set of standard axioms |
| CustomAxioms/HiddenInMacro | 🛑 1301ms (812ms)<br>CustomAxioms | 🟢 2423ms | 🛑 1266ms<br>LeanTestProject.CustomAxioms.HiddenInMacro.hidden_axiom is not in the allowed set of standard axioms |
| CustomAxioms/ProveAnything | 🛑 1289ms (781ms)<br>CustomAxioms | 🟢 2438ms | 🛑 1268ms<br>magic is not in the allowed set of standard axioms |
| CustomAxioms/ProveFalse | 🛑 1282ms (810ms)<br>CustomAxioms | 🟢 2452ms | 🛑 1314ms<br>exploit_axiom is not in the allowed set of standard axioms |
| CustomAxioms/SkipKernelTC | 🛑 1311ms (782ms)<br>CustomAxioms | 🟢 2456ms | 🟢 1290ms |
| Extern/BuiltinInit | 🛑 1580ms (797ms)<br>Extern | 🟢 2452ms | 🟢 1287ms |
| Extern/CoreNamespace | 🛑 1301ms (787ms)<br>CustomAxioms; Extern | 🟢 2442ms | 🛑 1286ms<br>exploit_axiom is not in the allowed set of standard axioms |
| Extern/ExportC | 🛑 1293ms (788ms)<br>CustomAxioms; Extern | 🟢 2438ms | 🛑 1278ms<br>exploit_axiom is not in the allowed set of standard axioms |
| Extern/ExternFFI | 🛑 1310ms (794ms)<br>CustomAxioms; Extern | 🟢 2443ms | 🛑 1267ms<br>exploit_axiom is not in the allowed set of standard axioms |
| Extern/InitHook | 🛑 1502ms (800ms)<br>Extern | 🟢 2459ms | 🟢 1284ms |
| Extern/PrivateExtern | 🛑 1309ms (781ms)<br>CustomAxioms; Extern | 🟢 2443ms | 🛑 1288ms<br>exploit_axiom is not in the allowed set of standard axioms |
| ImplementedBy/ChainedReplacement | 🛑 1297ms (821ms)<br>CustomAxioms; Extern; ImplementedBy | 🟢 2444ms | 🛑 1261ms<br>exploit_axiom is not in the allowed set of standard axioms |
| ImplementedBy/DirectReplacement | 🛑 1285ms (783ms)<br>CustomAxioms; ImplementedBy | 🟢 2455ms | 🛑 1274ms<br>exploit_axiom is not in the allowed set of standard axioms |
| ImplementedBy/PrivateImpl | 🛑 1353ms (786ms)<br>CustomAxioms; ImplementedBy | 🟢 2444ms | 🛑 1266ms<br>exploit_axiom is not in the allowed set of standard axioms |
| KernelRejection/NonPositive | 🛑 653ms (655ms)<br>KernelRejection | 🛑 2286ms<br>Could not find any oleans for: LeanTestProject.KernelRejection.NonPositive | 🟡 N/A<br>error during verification |
| KernelRejection/UnsafeCast | 🛑 657ms (647ms)<br>KernelRejection | 🛑 2313ms<br>Could not find any oleans for: LeanTestProject.KernelRejection.UnsafeCast | 🟡 N/A<br>error during verification |
| Metavariables/Timeout | 🛑 1296ms (788ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2444ms | 🛑 1267ms<br>sorryAx is not in the allowed set of standard axioms |
| Metavariables/TypeclassFail | 🛑 1320ms (790ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2461ms | 🛑 1266ms<br>sorryAx is not in the allowed set of standard axioms |
| NativeComputation/NativeDecide | 🛑 1431ms (785ms)<br>CustomAxioms; NativeComputation; Replay | 🛑 2423ms<br>(kernel) (interpreter) unknown declaration 'exploit_theorem._nativeDecide_1_1' | 🛑 1281ms<br>(kernel) (interpreter) unknown declaration 'exploit_theorem._nativeDecide_1_1' |
| NativeComputation/OfReduce | 🛑 1745ms (933ms)<br>CustomAxioms; NativeComputation; Replay | 🛑 2582ms<br>(kernel) (interpreter) unknown declaration 'exploit_theorem._nativeDecide_1_1' | 🛑 1381ms<br>(kernel) (interpreter) unknown declaration 'exploit_theorem._nativeDecide_1_1' |
| Partial/NonTerminating | 🛑 1305ms (793ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2414ms | 🛑 1280ms<br>sorryAx is not in the allowed set of standard axioms |
| RecursorIntegrity/MissingRecursor | 🛑 1174ms (786ms)<br>ConstructorIntegrity; CustomAxioms; RecursorIntegrity | 🟢 2472ms | 🛑 1278ms<br>definition exploit_theorem does not match the requirement |
| Sorry/Admit | 🛑 1348ms (787ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2435ms | 🛑 1276ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/ByAsSorry | 🛑 1316ms (799ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2433ms | 🛑 1285ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/Direct | 🛑 1286ms (788ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2459ms | 🛑 1283ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/Intermediate | 🛑 1384ms (783ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2429ms | 🛑 1278ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/Opaque | 🛑 3154ms (1182ms)<br>CustomAxioms; Sorry | 🟢 2866ms | 🛑 1658ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/ProofAsSorry | 🛑 1308ms (781ms)<br>CustomAxioms; Sorry | 🟢 2406ms | 🛑 1283ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/TerminalTactics | 🛑 1320ms (796ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2471ms | 🛑 1275ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/Underscore | 🛑 1305ms (795ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2432ms | 🛑 1293ms<br>sorryAx is not in the allowed set of standard axioms |
| SourcePatterns/LocalInstance | 🛑 1288ms (786ms)<br>SourcePatterns | 🟢 2433ms | 🛑 1268ms<br>theorem LeanTestProject.SourcePatterns.LocalInstance.exploit_theorem does not... |
| SourcePatterns/LocalInstanceArithmetic | 🛑 1292ms (787ms)<br>SourcePatterns | 🟢 2396ms | 🛑 1302ms<br>theorem exploit_theorem does not have the same type as the requirement |
| SourcePatterns/LocalMacroRules | 🛑 1297ms (788ms)<br>CustomAxioms; SourcePatterns | 🟢 2418ms | 🛑 1272ms<br>LeanTestProject.SourcePatterns.LocalMacroRules.hidden_axiom is not in the allowed set of standard axioms |
| SourcePatterns/LocalNotation | 🛑 1295ms (795ms)<br>SourcePatterns | 🟢 2425ms | 🛑 1300ms<br>exploit detected |
| SourcePatterns/NotationRedefinition | 🛑 1286ms (776ms)<br>CustomAxioms; SourcePatterns | 🟢 2429ms | 🛑 1320ms<br>theorem LeanTestProject.SourcePatterns.NotationRedefinition.exploit_theorem d... |
| SourcePatterns/ScopedNotation | 🛑 1330ms (832ms)<br>CustomAxioms; SourcePatterns | 🟢 2418ms | 🛑 1285ms<br>exploit detected |
| Transitive/DeepAxiom_L1 | 🛑 1689ms (782ms)<br>CustomAxioms | 🟢 2463ms | 🛑 1265ms<br>custom_axiom is not in the allowed set of standard axioms |
| Transitive/DeepSorry_L1 | 🛑 1686ms (801ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2404ms | 🛑 1282ms<br>sorryAx is not in the allowed set of standard axioms |
| Transitive/DeepSorry_L2 | 🛑 2053ms (814ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2471ms | 🛑 1312ms<br>sorryAx is not in the allowed set of standard axioms |
| Transitive/Level2_UsesBoth | 🟢 1656ms (1681ms) | 🟢 2418ms | 🟢 1278ms |
| Transitive/UsesBadLib | 🛑 1576ms (788ms)<br>CustomAxioms | 🟢 2428ms | 🛑 1293ms<br>BadLib.hiddenAssumption is not in the allowed set of standard axioms |
| Unsafe/UnsafeDefinition | 🛑 1287ms (790ms)<br>CustomAxioms; ImplementedBy; Unsafe | 🟢 2375ms | 🛑 1295ms<br>exploit_axiom is not in the allowed set of standard axioms |
| Valid/Dependencies | 🟢 1643ms (1651ms) | 🟢 2442ms | 🟢 1331ms |
| Valid/Helper | 🟢 1358ms (1359ms) | 🟢 2511ms | 🟢 1360ms |
| Valid/Simple | 🟢 1462ms (1408ms) | 🟢 2510ms | 🟢 1311ms |
| Valid/UnsafeReducibility | 🟢 1353ms (1367ms) | 🟢 2515ms | 🟢 1358ms |
| Valid/WithAxioms | 🟢 1488ms (1486ms) | 🟢 2528ms | 🟢 1305ms |

---

### Legend

- 🛑 **Detected**: Tool identified an exploit
- 🟢 **Passed**: Tool did not detect any exploit
- 🟡 **N/A**: Test setup issue or methodology limitation

**Time Format**: For LeanParanoia: `full_time (fail-fast_time)`

Note: WIP, might contain inaccuracies.