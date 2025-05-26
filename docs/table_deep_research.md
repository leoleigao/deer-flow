# Table Deep Research Prompts

The prompt assets for the Table‑Deep‑Research pipeline live under
`prompts/my_agents/table/`.
They are loaded by the planner and researcher nodes at runtime.

## Prompt files

- **plan.md** – creates a JSON plan of subtasks for the researcher.
- **glean_reader.md** – extracts insights from each document chunk.
- **reporter.md** – compiles the final Markdown guide.

Snapshot files for these templates are stored under
`tests/table_research/__snapshots__` and are checked in the test suite.
To update them when editing prompts run:

```bash
python tests/table_research/test_prompts_snapshot.py --snapshot-update
```

