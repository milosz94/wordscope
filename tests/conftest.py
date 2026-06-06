"""Mock heavy ML dependencies so tests can import src modules without spacy/stanza."""
import sys
from unittest.mock import MagicMock

for _mod in ("spacy", "stanza"):
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()
