import spacy
import re
import stanza
import json
from collections import Counter
from src.utils import extract_text, bigrams, detect_language
import os
import sys
import argparse

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

    raw_ents = {}
    for ent in doc.ents:
        raw_ents.setdefault(ent.label_, []).append(ent.text)
    entities = {label: Counter(texts).most_common(20) for label, texts in raw_ents.items()}

    return freqs, bi, metaphors, entities


def analyze_stanza(text):
    """Fallback analyzer using Stanza (for Serbian)."""
    stanza.download("sr", verbose=False)
    nlp = stanza.Pipeline("sr", processors="tokenize,pos,lemma,ner", use_gpu=False)
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

    raw_ents = {}
    for sentence in doc.sentences:
        for ent in sentence.ents:
            raw_ents.setdefault(ent.type, []).append(ent.text)
    entities = {label: Counter(texts).most_common(20) for label, texts in raw_ents.items()}

    return freqs, bi, metaphors, entities


def save_json(path, freqs, clusters, metaphors):
    os.makedirs("outputs", exist_ok=True)
    data = {
        "frequencies": {
            cat: [{"word": w, "count": c} for w, c in vals]
            for cat, vals in freqs.items()
        },
        "clusters": [{"words": list(pair), "count": c} for pair, c in clusters],
        "metaphors": metaphors,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_results(path, freqs, clusters, metaphors, entities):
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

        f.write("\n=== NAMED ENTITIES ===\n")
        if entities:
            for label in sorted(entities):
                f.write(f"\n  [{label}]\n")
                for text, count in entities[label]:
                    f.write(f"  {text}: {count}\n")
        else:
            f.write("(none detected)\n")


def save_results_md(path, freqs, clusters, metaphors):
    os.makedirs("outputs", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("# WordScope Analysis\n\n")

        for cat, vals in freqs.items():
            f.write(f"## {cat.capitalize()}\n\n")
            if vals:
                f.write("| Word | Count |\n")
                f.write("|------|-------|\n")
                for w, c in vals:
                    f.write(f"| {w} | {c} |\n")
            else:
                f.write("_No entries found._\n")
            f.write("\n")

        f.write("## Common Word Clusters\n\n")
        if clusters:
            f.write("| Cluster | Count |\n")
            f.write("|---------|-------|\n")
            for (a, b), c in clusters:
                f.write(f"| {a} {b} | {c} |\n")
        else:
            f.write("_No clusters found._\n")
        f.write("\n")

        f.write("## Possible Metaphors / Wordplay\n\n")
        if metaphors:
            for m in metaphors:
                f.write("- " + m.strip() + "\n")
        else:
            f.write("_No metaphors detected._\n")
        f.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WordScope: cross-lingual text analysis")
    parser.add_argument("input", help="Path to .docx file")
    parser.add_argument(
        "--format",
        choices=["txt", "md"],
        default="txt",
        help="Output format: txt (default) or md (Markdown)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Also export analysis as JSON to outputs/<name>.json",
    )
    args = parser.parse_args()

    input_path = args.input
    export_json = args.json
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
            freqs, clusters, metaphors, entities = analyze_spacy(text, lang_model)
        except Exception:
            print("🔁 Falling back to Stanza for Serbian...")
            freqs, clusters, metaphors, entities = analyze_stanza(text)
    else:
        freqs, clusters, metaphors, entities = analyze_spacy(text, lang_model)

    base_name = os.path.basename(input_path).replace(".docx", "")
    ext = args.format
    output_file = os.path.join("outputs", f"{base_name}_analysis.{ext}")

    if ext == "md":
        save_results_md(output_file, freqs, clusters, metaphors)
    else:
        save_results(output_file, freqs, clusters, metaphors, entities)

    print(f"✅ Analysis complete! Results saved to: {output_file}")

    if export_json:
        json_file = os.path.join("outputs", base_name + ".json")
        save_json(json_file, freqs, clusters, metaphors)
        print(f"✅ JSON export saved to: {json_file}")
