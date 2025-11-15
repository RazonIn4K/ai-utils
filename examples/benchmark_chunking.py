"""Benchmark heuristics for chunking and token estimation.

Run this script to measure how long chunking/token estimation takes on large
synthetic documents. Helpful when presenting performance characteristics in RFPs
or proposals.
"""

from __future__ import annotations

import argparse
import statistics
import time
from pathlib import Path

from ai_utils import estimate_token_count, split_into_chunks


def build_document(word_count: int) -> str:
    base_sentence = (
        "Natural language processing enables automation across industries, "
        "unlocking structured data from messy transcripts and documents."
    )
    sentences = [base_sentence for _ in range(max(1, word_count // len(base_sentence.split())))]
    return " \n".join(sentences)


def time_function(func, *args, runs: int = 3, **kwargs) -> tuple[float, float]:
    timings = []
    for _ in range(runs):
        start = time.perf_counter()
        func(*args, **kwargs)
        timings.append(time.perf_counter() - start)
    return min(timings), statistics.mean(timings)


def main(word_count: int, max_tokens: int, overlap: int) -> None:
    document = build_document(word_count)
    print(f"Benchmarking with ~{word_count} words (~{len(document)/1000:.1f}KB of text)")

    best, avg = time_function(estimate_token_count, document)
    print(f"estimate_token_count: best={best*1000:.2f}ms  avg={avg*1000:.2f}ms")

    def run_chunking() -> None:
        split_into_chunks(document, max_tokens=max_tokens, overlap_tokens=overlap)

    best, avg = time_function(run_chunking)
    print(f"split_into_chunks:   best={best:.3f}s   avg={avg:.3f}s  (max_tokens={max_tokens}, overlap={overlap})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark ai-utils chunking/token estimation")
    parser.add_argument("--words", type=int, default=50_000, help="Approximate number of words to generate")
    parser.add_argument("--max-tokens", type=int, default=400, help="Chunk size passed to split_into_chunks")
    parser.add_argument("--overlap", type=int, default=60, help="Overlap tokens between chunks")
    args = parser.parse_args()

    main(args.words, args.max_tokens, args.overlap)
