"""Aggregate chunk-level insights into a single summary structure."""

from __future__ import annotations

from collections import Counter
from datetime import date
from typing import Any, Iterable, Mapping


def merge_insights(
    chunk_outputs: Iterable[Mapping[str, Any]],
    glean_docs: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Merge LLM JSON outputs and compute freshness ranking."""
    seen: set[str] = set()
    insights: list[str] = []
    usage = Counter()

    for output in chunk_outputs:
        for ins in output.get("insights", []):
            norm = ins.strip().casefold()
            if norm not in seen:
                seen.add(norm)
                insights.append(ins.strip())
        for ex in output.get("usage_examples", []):
            usage[ex.strip()] += 1

    usage_examples = [ex for ex, _ in usage.most_common()]

    today = date.today()
    freshest: int | None = None
    for doc in glean_docs:
        ts = doc.get("last_updated")
        if not ts:
            continue
        try:
            days = (today - date.fromisoformat(ts)).days
        except Exception:
            continue
        freshest = days if freshest is None or days < freshest else freshest
    if freshest is None:
        sla = "cold"
    elif freshest <= 7:
        sla = "hot"
    elif freshest <= 30:
        sla = "warm"
    else:
        sla = "cold"

    return {
        "insights": insights,
        "usage_examples": usage_examples,
        "freshness_sla": sla,
    }
