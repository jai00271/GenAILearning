"""FOUND-101 — sequential vs gather async helpers (solution)."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


async def run_sequential(
    make_coro: Callable[[int], Awaitable[T]],
    n: int,
) -> list[T]:
    """Await make_coro(0)..make_coro(n-1) one after another; return results."""
    out: list[T] = []
    for i in range(n):
        out.append(await make_coro(i))
    return out


async def run_gather(
    make_coro: Callable[[int], Awaitable[T]],
    n: int,
) -> list[T]:
    """Schedule make_coro(0)..make_coro(n-1) with asyncio.gather; return results."""
    results = await asyncio.gather(*(make_coro(i) for i in range(n)))
    return list(results)


async def demo_sleep(i: int, delay: float = 0.05) -> int:
    """Tiny helper used by tests / demos."""
    await asyncio.sleep(delay)
    return i
