"""Utility to split text into token-budget aware chunks."""

from __future__ import annotations

from collections.abc import Callable, Iterable


def default_token_len(text: str) -> int:
    """Rudimentary token length estimator (word count)."""
    return len(text.split())


def smart_split(
    text: str,
    chunk_tokens: int,
    *,
    tiktoken_len: Callable[[str], int] = default_token_len,
) -> Iterable[str]:
    """Yield chunks of ``text`` each under ``chunk_tokens`` tokens."""
    if chunk_tokens <= 0:
        raise ValueError("chunk_tokens must be positive")

    parts = text.split("\n\n")
    current: list[str] = []
    tokens = 0
    for part in parts:
        length = tiktoken_len(part)
        # part itself exceeds budget
        if length > chunk_tokens:
            if current:
                yield "\n\n".join(current)
                current, tokens = [], 0
            yield part
            continue
        if tokens + length > chunk_tokens:
            if current:
                yield "\n\n".join(current)
            current, tokens = [part], length
        else:
            current.append(part)
            tokens += length
    if current:
        yield "\n\n".join(current)
