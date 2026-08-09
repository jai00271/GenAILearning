"""CORE 201 — teaching-scale BPE (starter).

Corpus words are whitespace-tokenized strings. We treat each word as a list of
characters plus an end-of-word marker '</w>', then repeatedly merge the most
frequent adjacent pair across the corpus.

Ties: if multiple pairs share the max frequency, pick the lexicographically
smallest pair (tuple of two strings) so results are deterministic.
"""

from __future__ import annotations


def word_to_symbols(word: str) -> list[str]:
    """'lowest' → ['l', 'o', 'w', 'e', 's', 't', '</w>']"""
    # TODO
    raise NotImplementedError


def learn_merges(corpus: list[str], num_merges: int) -> list[tuple[str, str]]:
    """Return a list of merge pairs in the order learned."""
    # TODO
    raise NotImplementedError


def apply_merges(word: str, merges: list[tuple[str, str]]) -> list[str]:
    """Encode one word by applying merges in order (leftmost match each pass)."""
    # TODO
    raise NotImplementedError
