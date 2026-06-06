"""Tests for the Named Entity Recognition section added to src/analyze.py."""
import sys
import os
import tempfile
from collections import Counter
from unittest.mock import MagicMock, patch, call

# Stub out spacy and stanza before importing the module under test
sys.modules.setdefault("spacy", MagicMock())
sys.modules.setdefault("stanza", MagicMock())

from src.analyze import analyze_spacy, analyze_stanza, save_results  # noqa: E402


def _make_token(text, pos_, lemma_, is_alpha=True):
    t = MagicMock()
    t.text = text
    t.pos_ = pos_
    t.lemma_ = lemma_.lower()
    t.is_alpha = is_alpha
    return t


def _make_entity(text, label_):
    e = MagicMock()
    e.text = text
    e.label_ = label_
    return e


def _make_sentence_spacy(text, ents=None):
    s = MagicMock()
    s.text = text
    return s


# ---------------------------------------------------------------------------
# analyze_spacy – NER extraction
# ---------------------------------------------------------------------------

class TestAnalyzeSpacyNER:
    def _build_doc(self, ents):
        """Return a mock spaCy doc with the given (text, label) entity pairs."""
        doc = MagicMock()
        doc.__iter__ = MagicMock(return_value=iter([]))
        doc.ents = [_make_entity(t, l) for t, l in ents]
        doc.sents = iter([])
        return doc

    def test_entities_grouped_by_label(self):
        mock_doc = self._build_doc([
            ("Copenhagen", "GPE"),
            ("Denmark", "GPE"),
            ("Hans Christian Andersen", "PER"),
        ])
        with patch("src.analyze.spacy") as mock_spacy:
            mock_nlp = MagicMock(return_value=mock_doc)
            mock_spacy.load.return_value = mock_nlp
            _, _, _, entities = analyze_spacy("some text", "da_core_news_lg")

        assert "GPE" in entities
        assert "PER" in entities
        assert len(entities["GPE"]) == 2  # 2 distinct GPE values
        # most common GPE first — both appear once so either order is fine
        gpe_texts = {text for text, _ in entities["GPE"]}
        assert gpe_texts == {"Copenhagen", "Denmark"}

    def test_repeated_entity_counted(self):
        mock_doc = self._build_doc([
            ("Copenhagen", "GPE"),
            ("Copenhagen", "GPE"),
            ("Copenhagen", "GPE"),
            ("Aarhus", "GPE"),
        ])
        with patch("src.analyze.spacy") as mock_spacy:
            mock_spacy.load.return_value = MagicMock(return_value=mock_doc)
            _, _, _, entities = analyze_spacy("some text", "da_core_news_lg")

        gpe = dict(entities["GPE"])
        assert gpe["Copenhagen"] == 3
        assert gpe["Aarhus"] == 1

    def test_no_entities_returns_empty_dict(self):
        mock_doc = self._build_doc([])
        with patch("src.analyze.spacy") as mock_spacy:
            mock_spacy.load.return_value = MagicMock(return_value=mock_doc)
            _, _, _, entities = analyze_spacy("some text", "da_core_news_lg")

        assert entities == {}

    def test_entities_capped_at_20_per_label(self):
        pairs = [(f"Place{i}", "GPE") for i in range(25)]
        mock_doc = self._build_doc(pairs)
        with patch("src.analyze.spacy") as mock_spacy:
            mock_spacy.load.return_value = MagicMock(return_value=mock_doc)
            _, _, _, entities = analyze_spacy("some text", "da_core_news_lg")

        assert len(entities["GPE"]) <= 20


# ---------------------------------------------------------------------------
# analyze_stanza – NER extraction
# ---------------------------------------------------------------------------

def _make_stanza_word(text, upos, lemma):
    w = MagicMock()
    w.text = text
    w.upos = upos
    w.lemma = lemma
    return w


def _make_stanza_entity(text, ent_type):
    e = MagicMock()
    e.text = text
    e.type = ent_type
    return e


def _make_stanza_sentence(text, words=None, ents=None):
    s = MagicMock()
    s.text = text
    s.words = words or []
    s.ents = ents or []
    return s


class TestAnalyzeStanzaNER:
    def _build_stanza_doc(self, sentences):
        doc = MagicMock()
        doc.sentences = sentences
        return doc

    def test_entities_grouped_by_type(self):
        sentences = [
            _make_stanza_sentence(
                "Beograd je lep grad.",
                ents=[
                    _make_stanza_entity("Beograd", "LOC"),
                    _make_stanza_entity("Srbija", "LOC"),
                ],
            ),
            _make_stanza_sentence(
                "Nikola Tesla je bio genije.",
                ents=[_make_stanza_entity("Nikola Tesla", "PER")],
            ),
        ]
        with patch("src.analyze.stanza") as mock_stanza:
            mock_stanza.Pipeline.return_value = MagicMock(return_value=self._build_stanza_doc(sentences))
            _, _, _, entities = analyze_stanza("some text")

        assert "LOC" in entities
        assert "PER" in entities
        loc_texts = {text for text, _ in entities["LOC"]}
        assert loc_texts == {"Beograd", "Srbija"}

    def test_repeated_stanza_entity_counted(self):
        sentences = [
            _make_stanza_sentence(
                "Beograd Beograd Novi Sad.",
                ents=[
                    _make_stanza_entity("Beograd", "LOC"),
                    _make_stanza_entity("Beograd", "LOC"),
                    _make_stanza_entity("Novi Sad", "LOC"),
                ],
            ),
        ]
        with patch("src.analyze.stanza") as mock_stanza:
            mock_stanza.Pipeline.return_value = MagicMock(return_value=self._build_stanza_doc(sentences))
            _, _, _, entities = analyze_stanza("some text")

        loc = dict(entities["LOC"])
        assert loc["Beograd"] == 2
        assert loc["Novi Sad"] == 1

    def test_no_entities_returns_empty_dict(self):
        sentences = [_make_stanza_sentence("Tekst.", ents=[])]
        with patch("src.analyze.stanza") as mock_stanza:
            mock_stanza.Pipeline.return_value = MagicMock(return_value=self._build_stanza_doc(sentences))
            _, _, _, entities = analyze_stanza("some text")

        assert entities == {}

    def test_ner_processor_in_pipeline(self):
        """Ensure the Stanza pipeline is created with the 'ner' processor."""
        sentences = [_make_stanza_sentence("Test.", ents=[])]
        with patch("src.analyze.stanza") as mock_stanza:
            mock_pipeline = MagicMock(return_value=MagicMock(sentences=sentences))
            mock_stanza.Pipeline.return_value = mock_pipeline
            analyze_stanza("some text")
            call_kwargs = mock_stanza.Pipeline.call_args
            processors_arg = call_kwargs[1].get("processors", "") if call_kwargs[1] else ""
            if not processors_arg:
                processors_arg = call_kwargs[0][1] if len(call_kwargs[0]) > 1 else ""
            assert "ner" in processors_arg


# ---------------------------------------------------------------------------
# save_results – NER section in output file
# ---------------------------------------------------------------------------

class TestSaveResultsNER:
    def _run_save(self, entities):
        freqs = {"nouns": [("hus", 3)]}
        clusters = [(("for", "at"), 2)]
        metaphors = []
        with tempfile.NamedTemporaryFile(
            mode="r", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            path = f.name
        try:
            save_results(path, freqs, clusters, metaphors, entities)
            with open(path, encoding="utf-8") as f:
                return f.read()
        finally:
            os.unlink(path)

    def test_ner_section_header_present(self):
        content = self._run_save({})
        assert "=== NAMED ENTITIES ===" in content

    def test_none_detected_when_empty(self):
        content = self._run_save({})
        assert "(none detected)" in content

    def test_entity_label_and_text_written(self):
        entities = {"PER": [("Hans", 2), ("Maria", 1)], "GPE": [("Copenhagen", 5)]}
        content = self._run_save(entities)
        assert "[GPE]" in content
        assert "[PER]" in content
        assert "Hans: 2" in content
        assert "Copenhagen: 5" in content

    def test_labels_sorted_alphabetically(self):
        entities = {"ORG": [("UN", 1)], "GPE": [("Berlin", 2)], "PER": [("Anna", 3)]}
        content = self._run_save(entities)
        gpe_pos = content.index("[GPE]")
        org_pos = content.index("[ORG]")
        per_pos = content.index("[PER]")
        assert gpe_pos < org_pos < per_pos
