## Task: JSON export of analysis
Date: 2026-06-06T17:28:28Z
Branch: agent/json-export-of-analysis-20260606-1725

DECIDED: Used a flat `--json` flag rather than `--format json` because the task spec says `--json` explicitly, and keeping it additive (both `.txt` and `.json` written when `--json` is passed) avoids breaking the documented default behavior.
NOTICED: The `analyze_stanza` fallback calls `stanza.download("sr")` on every invocation — it should check first or be called once at setup time. Also, `requirements.txt` is referenced in `setup.sh` but the file doesn't exist in the repo.
UNCERTAIN: The JSON output path convention `outputs/<name>.json` (not `outputs/<name>_analysis.json`) — I matched what the task description implied; the `.txt` file uses `_analysis` suffix but the task said just `<name>.json`.
WISHED_FOR: An installed Python environment with the project dependencies, so the full CLI path could be exercised end-to-end rather than just unit-testing the serialization logic.
