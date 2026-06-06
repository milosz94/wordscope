## Task: Markdown report output
Date: 2026-06-06T17:27:55Z
Branch: agent/markdown-report-output-20260606-1724

DECIDED: Used `argparse` instead of the existing raw `sys.argv` parsing because `--format {txt,md}` requires named optional arguments — argparse handles validation (choice enforcement, help text) cleanly without extra code. The default stays `txt` so existing usage (`python -m src.analyze file.docx`) is fully backwards-compatible.

NOTICED: The `analyze_stanza` fallback calls `stanza.download("sr")` on every invocation, which will re-download the model each time even if already cached. This is a latency/bandwidth issue independent of this task. Also, the Serbian metaphor regex in `analyze_spacy` fires on "kao" (a very common Serbian preposition meaning "as"), which likely produces many false positives.

UNCERTAIN: The ROADMAP says "alongside the existing `.txt` output" — I interpreted this as the `--format md` flag producing a `.md` file *instead of* the `.txt` file (choosing one format per run), not writing both simultaneously. The description is ambiguous; writing both always would be an alternative interpretation.

WISHED_FOR: A working Python environment with the NLP packages installed would have let me do an end-to-end integration test with a real `.docx` file rather than just unit-testing the formatting functions.
