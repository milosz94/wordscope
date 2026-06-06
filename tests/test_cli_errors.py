import os
import sys
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.analyze import main
from src.utils import detect_language


# --- detect_language unit tests ---

def test_detect_language_empty_returns_none():
    assert detect_language("") is None


def test_detect_language_unknown_returns_none():
    # English text is neither Danish nor Serbian
    result = detect_language("hello world this is some English text for testing")
    assert result is None


# --- CLI error tests ---

def test_no_args_prints_usage_and_exits(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main([])
    assert exc_info.value.code == 1
    assert "Usage" in capsys.readouterr().out


def test_missing_file_prints_friendly_message_and_exits(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["does_not_exist.docx"])
    assert exc_info.value.code == 1
    out = capsys.readouterr().out
    assert "❌" in out
    assert "not found" in out.lower() or "does_not_exist" in out


def test_unsupported_format_txt_exits(capsys, tmp_path):
    txt_file = tmp_path / "document.txt"
    txt_file.write_text("some content")
    with pytest.raises(SystemExit) as exc_info:
        main([str(txt_file)])
    assert exc_info.value.code == 1
    out = capsys.readouterr().out
    assert "❌" in out
    assert ".txt" in out or "unsupported" in out.lower()


def test_unsupported_format_pdf_exits(capsys, tmp_path):
    pdf_file = tmp_path / "document.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 fake content")
    with pytest.raises(SystemExit) as exc_info:
        main([str(pdf_file)])
    assert exc_info.value.code == 1
    out = capsys.readouterr().out
    assert "❌" in out
    assert ".pdf" in out or "unsupported" in out.lower()


def test_unsupported_format_no_extension_exits(capsys, tmp_path):
    no_ext_file = tmp_path / "document"
    no_ext_file.write_text("content")
    with pytest.raises(SystemExit) as exc_info:
        main([str(no_ext_file)])
    assert exc_info.value.code == 1
    out = capsys.readouterr().out
    assert "❌" in out


def test_corrupted_docx_prints_friendly_message_and_exits(capsys, tmp_path):
    bad_docx = tmp_path / "broken.docx"
    bad_docx.write_bytes(b"not a real zip/docx file")
    with pytest.raises(SystemExit) as exc_info:
        main([str(bad_docx)])
    assert exc_info.value.code == 1
    out = capsys.readouterr().out
    assert "❌" in out


def test_undetected_language_warns_and_falls_back(capsys, tmp_path):
    import docx as python_docx
    doc = python_docx.Document()
    doc.add_paragraph("hello world")
    docx_path = tmp_path / "test.docx"
    doc.save(str(docx_path))

    with patch("src.analyze.detect_language", return_value=None), \
         patch("src.analyze.analyze_spacy", return_value=({}, [], [])), \
         patch("src.analyze.save_results"):
        main([str(docx_path)])

    out = capsys.readouterr().out
    assert "⚠️" in out or "could not be detected" in out.lower()
    assert "danish" in out.lower() or "default" in out.lower()
