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

    words = text.split()
    current: list[str] = []
    tokens = 0

    for word in words:
        word_tokens = tiktoken_len(word)
        if tokens + word_tokens > chunk_tokens:
            if current:
                yield " ".join(current)
            current, tokens = [word], word_tokens
        else:
            current.append(word)
            tokens += word_tokens

    if current:
        yield " ".join(current)
