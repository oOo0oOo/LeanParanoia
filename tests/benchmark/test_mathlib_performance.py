"""
Mathlib benchmark suite for LeanParanoia.

Exercises the full checker stack against a lightweight but non-trivial Mathlib
theorem both with and without replay enabled. The selected theorem is proven in
Mathlib itself, so we simply re-export it to keep the benchmark honest while
avoiding unsafe definitions.

Run with: pytest -m benchmark -v
Skip with: pytest -m "not benchmark" (default)

Note: First run will download Mathlib (~2GB) and may take 10-30 minutes.
"""

import time
import pytest


BENCHMARK_MODULE = "MathlibBenchmark.Benchmark"
BENCHMARK_THEOREMS = [
    "test_nat_succ",
    "test_factorial_succ",
]


@pytest.mark.benchmark
@pytest.mark.parametrize("theorem", BENCHMARK_THEOREMS)
def test_benchmark_full_checks_no_replay(mathlib_verifier, theorem):
    """Benchmark the full checker stack without trusting Mathlib or using replay."""
    start = time.time()
    result = mathlib_verifier.verify_theorem(
        BENCHMARK_MODULE,
        theorem,
        enable_replay=False,
    )
    elapsed = time.time() - start

    assert result.success, (
        f"Full verification failed for {theorem}. Errors: {result.errors}"
    )
    print(f"\n{theorem} - no replay: {elapsed:.3f}s")


@pytest.mark.benchmark
@pytest.mark.parametrize("theorem", BENCHMARK_THEOREMS)
def test_benchmark_full_checks_with_replay(mathlib_verifier, theorem):
    """Benchmark the same theorem but with replay enabled to capture overhead."""
    start = time.time()
    result = mathlib_verifier.verify_theorem(
        BENCHMARK_MODULE,
        theorem,
        enable_replay=True,
    )
    elapsed = time.time() - start

    assert result.success, (
        f"Full verification with replay failed for {theorem}. Errors: {result.errors}"
    )
    print(f"\n{theorem} - incl replay: {elapsed:.3f}s")
