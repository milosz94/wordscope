# WordScope

**WordScope** is a cross-lingual text analysis toolkit for Danish 🇩🇰 and Serbian 🇷🇸.  
It extracts linguistic patterns, top frequent words by category, collocations, and stylistic devices such as metaphors.

---

## 🚀 Installation

```bash
git clone https://github.com/<your-username>/wordscope.git
cd wordscope
bash setup.sh
```

## 🧠 Usage

To analyze a .docx file:

```bash
source venv/bin/activate
python -m src.analyze /path/to/your/file.docx
```

## 📊 Features

Word frequencies by POS (nouns, adjectives, adverbs, verbs, subjectives)

Word clusters / collocations

Simple metaphor & wordplay detection

Auto language detection (Danish / Serbian)

Works on any .docx file

## 🧩 Example

```bash
python -m src.analyze examples/danish.docx
python -m src.analyze examples/serbian.docx
```