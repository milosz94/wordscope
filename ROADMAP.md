# 🌍 WordScope — ROADMAP

The autocoding agent picks up any task marked *(agent-ready)*, implements it on a
branch, runs the test suite, and opens a pull request. Keep each task scoped to a
single PR with clear acceptance criteria.

**Format (required, one line each):**
`- [ ] **Title** — short description *(agent-ready)*`

All four parts are required: the leading `- [ ]` checkbox, the `**bold title**`,
a ` — ` before the description, and `*(agent-ready)*`. Markdown headings (`##`)
and plain bullets are NOT picked up.

## Agent-ready tasks

- [~] **Add pytest test suite for utils** — Create a `tests/` directory with pytest covering the helper functions in `src/utils.py`, add `pytest` to `requirements.txt`, and document running the tests in the README *(agent-ready)*
- [x] **Markdown report output** — Add a `--format {txt,md}` flag to `src/analyze.py` that writes a formatted Markdown report alongside the existing `.txt` output *(agent-ready)*
- [ ] **JSON export of analysis** — Add a `--json` flag that serializes the frequency tables, word clusters, and detected metaphors to `outputs/<name>.json` *(agent-ready)*
- [ ] **Graceful CLI errors** — Replace stack traces with friendly messages for missing files, unsupported file formats, and undetected language; cover the new behavior with tests *(agent-ready)*
- [ ] **Named Entity Recognition section** — Add an NER section to the analysis output using the existing spaCy (Danish) and Stanza (Serbian) models *(agent-ready)*
