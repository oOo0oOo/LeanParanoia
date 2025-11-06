# Exploit Test Files

**Note**: Each tool is designed for different purposes and performing according to its specifications.

## Tool Comparison Results

| Exploit | LeanParanoia | lean4checker | SafeVerify |
|---------|--------------|--------------|------------|
| CSimp/WithAxiom | 🛑 1289ms (804ms)<br>CSimp; CustomAxioms | 🟢 2435ms | 🛑 1296ms<br>exploit_axiom is not in the allowed set of standard axioms |
| CSimp/WithUnsafe | 🛑 1297ms (783ms)<br>CSimp; CustomAxioms | 🟢 2422ms | 🛑 1312ms<br>exploit_axiom is not in the allowed set of standard axioms |
| ConstructorIntegrity/ManualConstructor | 🛑 1168ms (798ms)<br>ConstructorIntegrity; CustomAxioms; RecursorIntegrity | 🟢 2401ms | 🛑 1287ms<br>definition exploit_theorem does not match the requirement |
| CustomAxioms/FakeStdLib | 🛑 3137ms (1145ms)<br>CustomAxioms | 🟢 2830ms | 🛑 1626ms<br>Std.TrustMe.forgedFalse is not in the allowed set of standard axioms |
| CustomAxioms/ForgeRunCmd | 🛑 3090ms (1150ms)<br>CustomAxioms | 🟢 2782ms | 🛑 1682ms<br>RunCmdForgedFalse is not in the allowed set of standard axioms |
| CustomAxioms/ForgeRunTac | 🛑 3100ms (1152ms)<br>CustomAxioms | 🟢 2799ms | 🛑 1625ms<br>RunTacForgedFalse is not in the allowed set of standard axioms |
| CustomAxioms/HiddenInInstance | 🛑 1288ms (779ms)<br>CustomAxioms | 🟢 2394ms | 🛑 1295ms<br>LeanTestProject.CustomAxioms.HiddenInInstance.hidden_axiom is not in the allowed set of standard axioms |
| CustomAxioms/HiddenInMacro | 🛑 1297ms (771ms)<br>CustomAxioms | 🟢 2414ms | 🛑 1265ms<br>LeanTestProject.CustomAxioms.HiddenInMacro.hidden_axiom is not in the allowed set of standard axioms |
| CustomAxioms/ProveAnything | 🛑 1285ms (785ms)<br>CustomAxioms | 🟢 2414ms | 🛑 1288ms<br>magic is not in the allowed set of standard axioms |
| CustomAxioms/ProveFalse | 🛑 1307ms (787ms)<br>CustomAxioms | 🟢 2410ms | 🛑 1285ms<br>exploit_axiom is not in the allowed set of standard axioms |
| CustomAxioms/SkipKernelTC | 🛑 1297ms (772ms)<br>CustomAxioms | 🟢 2410ms | 🟢 1260ms |
| Extern/BuiltinInit | 🛑 1591ms (773ms)<br>Extern | 🟢 2403ms | 🟢 1257ms |
| Extern/CoreNamespace | 🛑 1298ms (783ms)<br>CustomAxioms; Extern | 🟢 2411ms | 🛑 1254ms<br>exploit_axiom is not in the allowed set of standard axioms |
| Extern/ExportC | 🛑 1294ms (794ms)<br>CustomAxioms; Extern | 🟢 2442ms | 🛑 1290ms<br>exploit_axiom is not in the allowed set of standard axioms |
| Extern/ExternFFI | 🛑 1299ms (789ms)<br>CustomAxioms; Extern | 🟢 2414ms | 🛑 1268ms<br>exploit_axiom is not in the allowed set of standard axioms |
| Extern/InitHook | 🛑 1551ms (790ms)<br>Extern | 🟢 2462ms | 🟢 1275ms |
| Extern/PrivateExtern | 🛑 1298ms (791ms)<br>CustomAxioms; Extern | 🟢 2404ms | 🛑 1278ms<br>exploit_axiom is not in the allowed set of standard axioms |
| ImplementedBy/ChainedReplacement | 🛑 1320ms (780ms)<br>CustomAxioms; Extern; ImplementedBy | 🟢 2413ms | 🛑 1279ms<br>exploit_axiom is not in the allowed set of standard axioms |
| ImplementedBy/DirectReplacement | 🛑 1286ms (783ms)<br>CustomAxioms; ImplementedBy | 🟢 2419ms | 🛑 1279ms<br>exploit_axiom is not in the allowed set of standard axioms |
| ImplementedBy/PrivateImpl | 🛑 1299ms (784ms)<br>CustomAxioms; ImplementedBy | 🟢 2448ms | 🛑 1265ms<br>exploit_axiom is not in the allowed set of standard axioms |
| KernelRejection/NonPositive | 🛑 660ms (647ms)<br>KernelRejection | 🛑 2274ms<br>Could not find any oleans for: LeanTestProject.KernelRejection.NonPositive | 🟡 N/A<br>error during verification |
| KernelRejection/UnsafeCast | 🛑 666ms (648ms)<br>KernelRejection | 🛑 2257ms<br>Could not find any oleans for: LeanTestProject.KernelRejection.UnsafeCast | 🟡 N/A<br>error during verification |
| Metavariables/Timeout | 🛑 1298ms (774ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2401ms | 🛑 1271ms<br>sorryAx is not in the allowed set of standard axioms |
| Metavariables/TypeclassFail | 🛑 1320ms (777ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2414ms | 🛑 1269ms<br>sorryAx is not in the allowed set of standard axioms |
| NativeComputation/NativeDecide | 🛑 1395ms (784ms)<br>CustomAxioms; NativeComputation; Replay | 🛑 2391ms<br>(kernel) (interpreter) unknown declaration 'exploit_theorem._nativeDecide_1_1' | 🛑 1262ms<br>(kernel) (interpreter) unknown declaration 'exploit_theorem._nativeDecide_1_1' |
| NativeComputation/OfReduce | 🛑 1737ms (899ms)<br>CustomAxioms; NativeComputation; Replay | 🛑 2513ms<br>(kernel) (interpreter) unknown declaration 'exploit_theorem._nativeDecide_1_1' | 🛑 1393ms<br>(kernel) (interpreter) unknown declaration 'exploit_theorem._nativeDecide_1_1' |
| Partial/NonTerminating | 🛑 1311ms (780ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2429ms | 🛑 1270ms<br>sorryAx is not in the allowed set of standard axioms |
| RecursorIntegrity/MissingRecursor | 🛑 1162ms (782ms)<br>ConstructorIntegrity; CustomAxioms; RecursorIntegrity | 🟢 2448ms | 🛑 1286ms<br>definition exploit_theorem does not match the requirement |
| Sorry/Admit | 🛑 1310ms (782ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2460ms | 🛑 1262ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/ByAsSorry | 🛑 1313ms (800ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2418ms | 🛑 1268ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/Direct | 🛑 1310ms (769ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2439ms | 🛑 1260ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/Intermediate | 🛑 1370ms (778ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2444ms | 🛑 1282ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/Opaque | 🛑 3072ms (1144ms)<br>CustomAxioms; Sorry | 🟢 2803ms | 🛑 1670ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/ProofAsSorry | 🛑 1299ms (795ms)<br>CustomAxioms; Sorry | 🟢 2396ms | 🛑 1265ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/TerminalTactics | 🛑 1307ms (779ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2425ms | 🛑 1262ms<br>sorryAx is not in the allowed set of standard axioms |
| Sorry/Underscore | 🛑 1324ms (783ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2414ms | 🛑 1279ms<br>sorryAx is not in the allowed set of standard axioms |
| SourcePatterns/LocalInstance | 🛑 1295ms (778ms)<br>SourcePatterns | 🟢 2412ms | 🛑 1280ms<br>theorem LeanTestProject.SourcePatterns.LocalInstance.exploit_theorem does not... |
| SourcePatterns/LocalInstanceArithmetic | 🛑 1288ms (793ms)<br>SourcePatterns | 🟢 2433ms | 🛑 1254ms<br>theorem exploit_theorem does not have the same type as the requirement |
| SourcePatterns/LocalMacroRules | 🛑 1285ms (779ms)<br>CustomAxioms; SourcePatterns | 🟢 2411ms | 🛑 1265ms<br>LeanTestProject.SourcePatterns.LocalMacroRules.hidden_axiom is not in the allowed set of standard axioms |
| SourcePatterns/LocalNotation | 🛑 1307ms (792ms)<br>SourcePatterns | 🟢 2430ms | 🛑 1292ms<br>exploit detected |
| SourcePatterns/NotationRedefinition | 🛑 1288ms (769ms)<br>CustomAxioms; SourcePatterns | 🟢 2451ms | 🛑 1281ms<br>theorem LeanTestProject.SourcePatterns.NotationRedefinition.exploit_theorem d... |
| SourcePatterns/ScopedNotation | 🛑 1306ms (776ms)<br>CustomAxioms; SourcePatterns | 🟢 2430ms | 🛑 1289ms<br>exploit detected |
| Transitive/DeepAxiom_L1 | 🛑 1656ms (806ms)<br>CustomAxioms | 🟢 2421ms | 🛑 1273ms<br>custom_axiom is not in the allowed set of standard axioms |
| Transitive/DeepSorry_L1 | 🛑 1671ms (790ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2414ms | 🛑 1268ms<br>sorryAx is not in the allowed set of standard axioms |
| Transitive/DeepSorry_L2 | 🛑 2077ms (787ms)<br>CustomAxioms; Sorry; Unsafe | 🟢 2415ms | 🛑 1269ms<br>sorryAx is not in the allowed set of standard axioms |
| Transitive/Level2_UsesBoth | 🟢 1683ms (1674ms) | 🟢 2418ms | 🟢 1266ms |
| Transitive/UsesBadLib | 🛑 1609ms (792ms)<br>CustomAxioms | 🟢 2417ms | 🛑 1276ms<br>BadLib.hiddenAssumption is not in the allowed set of standard axioms |
| Unsafe/UnsafeDefinition | 🛑 1298ms (806ms)<br>CustomAxioms; ImplementedBy; Unsafe | 🟢 2403ms | 🛑 1275ms<br>exploit_axiom is not in the allowed set of standard axioms |
| Valid/Dependencies | 🟢 1655ms (1659ms) | 🟢 2435ms | 🟢 1263ms |
| Valid/Helper | 🟢 1305ms (1301ms) | 🟢 2419ms | 🟢 1261ms |
| Valid/Simple | 🟢 1355ms (1363ms) | 🟢 2414ms | 🟢 1272ms |
| Valid/UnsafeReducibility | 🟢 1292ms (1302ms) | 🟢 2461ms | 🟢 1299ms |
| Valid/WithAxioms | 🟢 1462ms (1437ms) | 🟢 2423ms | 🟢 1278ms |

---

### Legend

- 🛑 **Detected**: Tool identified an exploit
- 🟢 **Passed**: Tool did not detect any exploit
- 🟡 **N/A**: Test setup issue or methodology limitation

**Time Format**: For LeanParanoia: `full_time (fail-fast_time)`

Note: WIP, might contain inaccuracies.