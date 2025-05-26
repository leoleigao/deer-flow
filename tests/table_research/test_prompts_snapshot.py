from pathlib import Path

PROMPT_DIR = Path("prompts/my_agents/table")
SNAPSHOT_DIR = Path("tests/table_research/__snapshots__")


def render(name: str) -> str:
    text = (PROMPT_DIR / f"{name}.md").read_text()
    text = text.replace("{{ table_name }}", "demo.Table")
    text = text.replace("{{ locale }}", "en-US")
    text = text.replace("{{ chunk_tokens }}", "2048")
    return text


def test_plan_snapshot():
    rendered = render("plan")
    expected = (SNAPSHOT_DIR / "plan.md").read_text()
    assert rendered == expected


def test_glean_reader_snapshot():
    rendered = render("glean_reader")
    expected = (SNAPSHOT_DIR / "glean_reader.md").read_text()
    assert rendered == expected


def test_reporter_snapshot():
    rendered = render("reporter")
    expected = (SNAPSHOT_DIR / "reporter.md").read_text()
    assert rendered == expected
