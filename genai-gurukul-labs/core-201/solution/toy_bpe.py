"""CORE 201 — teaching-scale BPE (solution)."""

from __future__ import annotations

from collections import Counter


def word_to_symbols(word: str) -> list[str]:
    return list(word) + ["</w>"]


def _pair_counts(words: list[list[str]]) -> Counter[tuple[str, str]]:
    counts: Counter[tuple[str, str]] = Counter()
    for symbols in words:
        for i in range(len(symbols) - 1):
            counts[(symbols[i], symbols[i + 1])] += 1
    return counts


def _merge_word(symbols: list[str], pair: tuple[str, str]) -> list[str]:
    a, b = pair
    out: list[str] = []
    i = 0
    while i < len(symbols):
        if i < len(symbols) - 1 and symbols[i] == a and symbols[i + 1] == b:
            out.append(a + b)
            i += 2
        else:
            out.append(symbols[i])
            i += 1
    return out


def learn_merges(corpus: list[str], num_merges: int) -> list[tuple[str, str]]:
    words = [word_to_symbols(w) for w in corpus]
    merges: list[tuple[str, str]] = []
    for _ in range(num_merges):
        counts = _pair_counts(words)
        if not counts:
            break
        best_freq = max(counts.values())
        candidates = [p for p, c in counts.items() if c == best_freq]
        pair = min(candidates)
        merges.append(pair)
        words = [_merge_word(w, pair) for w in words]
    return merges


def apply_merges(word: str, merges: list[tuple[str, str]]) -> list[str]:
    symbols = word_to_symbols(word)
    for pair in merges:
        symbols = _merge_word(symbols, pair)
    return symbols
