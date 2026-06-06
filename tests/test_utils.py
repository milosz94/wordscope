"""Tests for src.utils: extract_text, bigrams, detect_language."""

import io
import os
import tempfile
from unittest.mock import patch

import docx
import pytest

from src.utils import bigrams, detect_language, extract_text


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_docx(*paragraphs: str) -> str:
    """Write a temporary .docx file with the given paragraphs and return its path."""
    doc = docx.Document()
    for para in paragraphs:
        doc.add_paragraph(para)
    tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
    doc.save(tmp.name)
    tmp.close()
    return tmp.name


# ---------------------------------------------------------------------------
# bigrams
# ---------------------------------------------------------------------------

class TestBigrams:
    def test_basic(self):
        assert bigrams(["a", "b", "c"]) == [("a", "b"), ("b", "c")]

    def test_two_elements(self):
        assert bigrams(["x", "y"]) == [("x", "y")]

    def test_single_element_returns_empty(self):
        assert bigrams(["a"]) == []

    def test_empty_returns_empty(self):
        assert bigrams([]) == []

    def test_returns_list(self):
        result = bigrams(["a", "b"])
        assert isinstance(result, list)

    def test_tuples_in_list(self):
        result = bigrams(["a", "b", "c"])
        for item in result:
            assert isinstance(item, tuple)
            assert len(item) == 2

    def test_with_integers(self):
        assert bigrams([1, 2, 3]) == [(1, 2), (2, 3)]

    def test_with_repeated_tokens(self):
        assert bigrams(["the", "the", "the"]) == [("the", "the"), ("the", "the")]

    def test_does_not_consume_generator(self):
        # bigrams receives a list; also works when passed a generator-like iterable
        result = bigrams(iter(["a", "b", "c"]))
        assert result == [("a", "b"), ("b", "c")]


# ---------------------------------------------------------------------------
# detect_language
# ---------------------------------------------------------------------------

class TestDetectLanguage:
    def test_danish_returns_danish_model(self):
        with patch("src.utils.detect", return_value="da"):
            assert detect_language("some text") == "da_core_news_lg"

    def test_danish_prefix_da_DK(self):
        with patch("src.utils.detect", return_value="da-DK"):
            assert detect_language("some text") == "da_core_news_lg"

    def test_serbian_returns_multilingual_model(self):
        with patch("src.utils.detect", return_value="sr"):
            assert detect_language("some text") == "xx_sent_ud_sm"

    def test_serbian_prefix_sr_Cyrl(self):
        with patch("src.utils.detect", return_value="sr-Cyrl"):
            assert detect_language("some text") == "xx_sent_ud_sm"

    def test_unknown_language_returns_none(self):
        with patch("src.utils.detect", return_value="fr"):
            assert detect_language("bonjour le monde") is None

    def test_exception_from_langdetect_returns_none(self):
        from langdetect import LangDetectException
        with patch("src.utils.detect", side_effect=LangDetectException(0, "failed")):
            assert detect_language("!!!") is None

    def test_general_exception_returns_none(self):
        with patch("src.utils.detect", side_effect=Exception("unexpected")):
            assert detect_language("???") is None

    def test_return_type_is_string(self):
        with patch("src.utils.detect", return_value="da"):
            result = detect_language("text")
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# extract_text
# ---------------------------------------------------------------------------

class TestExtractText:
    def test_single_paragraph(self):
        path = _make_docx("Hello world")
        try:
            text = extract_text(path)
            assert "Hello world" in text
        finally:
            os.unlink(path)

    def test_multiple_paragraphs_joined_with_newlines(self):
        path = _make_docx("First paragraph", "Second paragraph")
        try:
            text = extract_text(path)
            assert "First paragraph" in text
            assert "Second paragraph" in text
            assert "\n" in text
        finally:
            os.unlink(path)

    def test_empty_document(self):
        path = _make_docx()
        try:
            text = extract_text(path)
            assert isinstance(text, str)
        finally:
            os.unlink(path)

    def test_returns_string(self):
        path = _make_docx("Some content")
        try:
            result = extract_text(path)
            assert isinstance(result, str)
        finally:
            os.unlink(path)

    def test_paragraph_order_preserved(self):
        path = _make_docx("Alpha", "Beta", "Gamma")
        try:
            text = extract_text(path)
            assert text.index("Alpha") < text.index("Beta") < text.index("Gamma")
        finally:
            os.unlink(path)

    def test_unicode_content(self):
        path = _make_docx("Ære øl å ñ ü č š ž")
        try:
            text = extract_text(path)
            assert "Ære" in text
            assert "ñ" in text
        finally:
            os.unlink(path)

    def test_example_danish_file(self):
        """Integration test using the bundled Danish example file."""
        examples_dir = os.path.join(os.path.dirname(__file__), "..", "examples")
        danish_path = os.path.join(examples_dir, "danski.docx")
        if not os.path.exists(danish_path):
            pytest.skip("Danish example file not present")
        text = extract_text(danish_path)
        assert len(text) > 100
        assert isinstance(text, str)

    def test_example_serbian_file(self):
        """Integration test using the bundled Serbian example file."""
        examples_dir = os.path.join(os.path.dirname(__file__), "..", "examples")
        serbian_path = os.path.join(examples_dir, "srpski.docx")
        if not os.path.exists(serbian_path):
            pytest.skip("Serbian example file not present")
        text = extract_text(serbian_path)
        assert len(text) > 100
        assert isinstance(text, str)
