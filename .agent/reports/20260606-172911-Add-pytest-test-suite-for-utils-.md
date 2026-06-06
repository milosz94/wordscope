## Task: Add pytest test suite for utils
Date: 2026-06-06T17:29:12Z
Branch: agent/add-pytest-test-suite-for-utils-20260606-1723

DECIDED: Used `unittest.mock.patch` to control `langdetect.detect` in `detect_language` tests rather than relying on real language detection — this makes the tests fast, deterministic, and isolated from the underlying model's non-determinism. Used `tempfile`-based `.docx` construction for `extract_text` unit tests and kept the example-file tests as skippable integration tests.

NOTICED: `detect_language` will never return `xx_sent_ud_sm` for actual Serbian text run through the real stack, because `langdetect` returns `'hr'` (Croatian) for the Serbian example file — the `startswith("sr")` branch is unreachable in practice. This is a latent bug outside this task's scope.

UNCERTAIN: The README references `examples/danish.docx` and `examples/serbian.docx`, but the actual files are named `danski.docx` and `srpski.docx`. I used the real file names for integration tests and assumed the README has a documentation error rather than the files being misnamed.

WISHED_FOR: A `requirements-dev.txt` or `pyproject.toml` listing `pytest` as a dev dependency would have made setup unambiguous; I had to install packages manually with `--break-system-packages` due to no venv and a locked system Python.
