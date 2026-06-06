## Task: Graceful CLI errors
Date: 2026-06-06T17:35:48Z
Branch: agent/graceful-cli-errors-20260606-1728

DECIDED: Refactored the `__main__` block into a `main(argv=None)` function so error paths are directly unit-testable without subprocess overhead. The three new checks are ordered logically — extension first (so a missing non-.docx file still gets the format error, not "file not found"), then existence, then parse error on `extract_text()`. `detect_language()` now returns `None` instead of silently defaulting, giving the caller full control over user messaging.

NOTICED: `*.txt` is listed in `.gitignore`, which also catches `requirements.txt` — so no agent task can commit that file without a gitignore change. The "Add pytest test suite for utils" task is marked `[~]` and has the same constraint. The setup.sh references a non-existent `requirements.txt`, so first-time setup is broken for users who don't have spacy/stanza installed differently.

UNCERTAIN: Whether `detect_language()` returning `None` instead of defaulting to Danish is the right semantic change — the previous behaviour was intentional (silent fallback). I kept the fallback in `main()` but now it's visible to the user via a warning, which aligns with the task spec.

WISHED_FOR: A pinned Python environment (venv or container with deps installed) would have let me run tests immediately rather than needing to bootstrap pip and install packages manually.
