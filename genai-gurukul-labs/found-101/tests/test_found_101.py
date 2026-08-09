"""Tests for FOUND-101 labs. Imports starter or solution via GURUKUL_LAB."""

from __future__ import annotations

import importlib
import os
import sys
import time
from pathlib import Path

import numpy as np
import pytest
from pydantic import ValidationError

LAB = os.environ.get("GURUKUL_LAB", "starter")
ROOT = Path(__file__).resolve().parents[1]
LAB_DIR = ROOT / LAB


def _load(mod_name: str):
    sys.path.insert(0, str(LAB_DIR))
    # Drop cached modules from the other lab variant if present.
    for key in list(sys.modules):
        if key in {"similarity", "async_calls", "schemas"} or key.startswith(mod_name):
            if key.split(".")[0] in {"similarity", "async_calls", "schemas"}:
                del sys.modules[key]
    return importlib.import_module(mod_name)


similarity = _load("similarity")
async_calls = _load("async_calls")
schemas = _load("schemas")


def test_cosine_identical():
    v = np.array([1.0, 2.0, 3.0])
    assert similarity.cosine_similarity(v, v) == pytest.approx(1.0)


def test_cosine_orthogonal():
    assert similarity.cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)


def test_cosine_zero_vector():
    assert similarity.cosine_similarity([0.0, 0.0], [1.0, 2.0]) == 0.0


def test_most_similar_index():
    query = [1.0, 0.0]
    corpus = [[0.0, 1.0], [0.9, 0.1], [0.1, 0.9]]
    assert similarity.most_similar(query, corpus) == 1


@pytest.mark.asyncio
async def test_sequential_and_gather_results():
    async def make(i: int):
        return await async_calls.demo_sleep(i, delay=0.02)

    seq = await async_calls.run_sequential(make, 3)
    gathered = await async_calls.run_gather(make, 3)
    assert seq == [0, 1, 2]
    assert gathered == [0, 1, 2]


@pytest.mark.asyncio
async def test_gather_is_faster_than_sequential():
    delay = 0.05
    n = 4

    async def make(i: int):
        return await async_calls.demo_sleep(i, delay=delay)

    t0 = time.perf_counter()
    await async_calls.run_sequential(make, n)
    seq_dt = time.perf_counter() - t0

    t1 = time.perf_counter()
    await async_calls.run_gather(make, n)
    gather_dt = time.perf_counter() - t1

    assert seq_dt > delay * (n - 0.5)
    assert gather_dt < delay * 2.5
    assert gather_dt < seq_dt * 0.75


def test_chat_turn_ok():
    turn = schemas.ChatTurn(role="user", content="hello")
    assert turn.role == "user"
    assert turn.name is None


def test_chat_turn_rejects_empty_content():
    with pytest.raises(ValidationError):
        schemas.ChatTurn(role="user", content="")


def test_parse_turns():
    rows = [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hi", "name": "jai"},
    ]
    turns = schemas.parse_turns(rows)
    assert len(turns) == 2
    assert turns[1].name == "jai"


def test_parse_turns_invalid_role():
    with pytest.raises(ValidationError):
        schemas.parse_turns([{"role": "narrator", "content": "nope"}])
