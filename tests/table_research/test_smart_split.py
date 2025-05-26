from src.my_agents.table_research.smart_split import smart_split


def test_smart_split_respects_budget_and_order():
    text = "A B C D E F"

    def fake_len(t: str) -> int:
        return len(t.split())

    chunks = list(smart_split(text, 2, tiktoken_len=fake_len))
    assert chunks == ["A B", "C D", "E F"]
    assert " ".join(chunks) == text
    assert all(fake_len(c) <= 2 for c in chunks)
