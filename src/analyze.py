import spacy
import re
import stanza
from collections import Counter
from src.utils import extract_text, bigrams, detect_language
import os
import sys

def analyze_spacy(text, lang_model):
    """Analyzes text using a spaCy model."""
    nlp = spacy.load(lang_model)
    doc = nlp(text)

    words = [t.text.lower() for t in doc if t.is_alpha]
    pos_map = {
        "NOUN": "nouns",
        "ADJ": "adjectives",
        "ADV": "adverbs",
        "VERB": "verbs",
        "PRON": "subjectives"
    }

    results = {v: [] for v in pos_map.values()}
    for token in doc:
        if token.pos_ in pos_map:
            results[pos_map[token.pos_]].append(token.lemma_.lower())

    freqs = {k: Counter(v).most_common(50) for k, v in results.items()}
    bi = Counter(bigrams(words)).most_common(20)
    metaphors = [s.text for s in doc.sents if re.search(r"som en|ligesom|kao da|kao", s.text, re.IGNORECASE)]

    return freqs, bi, metaphors


def analyze_stanza(text):
    """Fallback analyzer using Stanza (for Serbian)."""
    stanza.download("sr", verbose=False)
    nlp = stanza.Pipeline("sr", use_gpu=False)
    doc = nlp(text)

    words = []
    pos_data = {"nouns": [], "adjectives": [], "adverbs": [], "verbs": [], "subjectives": []}

    for sentence in doc.sentences:
        for token in sentence.words:
            if token.upos in ["NOUN", "ADJ", "ADV", "VERB", "PRON"]:
                words.append(token.text.lower())
                if token.upos == "NOUN":
                    pos_data["nouns"].append(token.lemma)
                elif token.upos == "ADJ":
                    pos_data["adjectives"].append(token.lemma)
                elif token.upos == "ADV":
                    pos_data["adverbs"].append(token.lemma)
                elif token.upos == "VERB":
                    pos_data["verbs"].append(token.lemma)
                elif token.upos == "PRON":
                    pos_data["subjectives"].append(token.lemma)

    freqs = {k: Counter(v).most_common(50) for k, v in pos_data.items()}
    bi = Counter(bigrams(words)).most_common(20)
    metaphors = [s.text for s in doc.sentences if re.search(r"kao da|kao", s.text, re.IGNORECASE)]

    return freqs, bi, metaphors


def save_results(path, freqs, clusters, metaphors):
    os.makedirs("outputs", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for cat, vals in freqs.items():
            f.write(f"\n=== {cat.upper()} ===\n")
            for w, c in vals:
                f.write(f"{w}: {c}\n")

        f.write("\n=== COMMON WORD CLUSTERS ===\n")
        for (a, b), c in clusters:
            f.write(f"{a} {b}: {c}\n")

        f.write("\n=== POSSIBLE METAPHORS / WORDPLAY ===\n")
        for m in metaphors:
            f.write("- " + m + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.analyze <path_to_docx>")
        sys.exit(1)

    input_path = sys.argv[1]
    if not os.path.exists(input_path):
        print("❌ File not found:", input_path)
        sys.exit(1)

    print("📖 Reading:", input_path)
    text = extract_text(input_path)
    lang_model = detect_language(text)

    print(f"🌐 Detected language model: {lang_model}")

    if lang_model == "xx_sent_ud_sm":
        try:
            print("⚙️ Using spaCy multilingual model...")
            freqs, clusters, metaphors = analyze_spacy(text, lang_model)
        except Exception:
            print("🔁 Falling back to Stanza for Serbian...")
            freqs, clusters, metaphors = analyze_stanza(text)
    else:
        freqs, clusters, metaphors = analyze_spacy(text, lang_model)

    output_file = os.path.join("outputs", os.path.basename(input_path).replace(".docx", "_analysis.txt"))
    save_results(output_file, freqs, clusters, metaphors)

    print(f"✅ Analysis complete! Results saved to: {output_file}")
