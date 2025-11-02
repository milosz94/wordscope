# 🌍 WordScope

**WordScope** is a cross-lingual text analysis toolkit for Danish 🇩🇰 and Serbian 🇷🇸.
It extracts linguistic patterns, top frequent words by category, collocations, and stylistic devices such as metaphors.

---

## 🚀 Features

✅ Word frequencies by POS (nouns, adjectives, adverbs, verbs, subjectives)
✅ Word clusters / collocations
✅ Simple metaphor & wordplay detection
✅ Automatic language detection (Danish / Serbian)
✅ Works on any `.docx` file

---

## 🧩 Example

```
python -m src.analyze examples/danish.docx
python -m src.analyze examples/serbian.docx
```

The results will be saved in:

```
outputs/<filename>_analysis.txt
```

---

# ⚙️ Installation

## 🐧 Linux / macOS

```
git clone https://github.com/milosz94/wordscope.git
cd wordscope
bash setup.sh
```

Then activate your environment:

```
source venv/bin/activate
```

To analyze a `.docx` file:

```
python -m src.analyze /path/to/your/file.docx
```

---

## 🪟 Windows

🧠 Requirements:

* Python 3.10 or newer
* Git
* pip
* Microsoft Visual C++ Build Tools ([https://visualstudio.microsoft.com/visual-cpp-build-tools/](https://visualstudio.microsoft.com/visual-cpp-build-tools/))

### 1️⃣ Clone the repository

Open PowerShell or Git Bash:

```
git clone https://github.com/milosz94/wordscope.git
cd wordscope
```

### 2️⃣ Create a virtual environment

```
python -m venv venv
venv\Scripts\activate
```

You should now see `(venv)` at the beginning of your prompt.

### 3️⃣ Install dependencies

```
pip install --upgrade pip
pip install -r requirements.txt
```

### 4️⃣ Download language models

```
python -m spacy download da_core_news_lg
pip install https://github.com/explosion/spacy-models/releases/download/xx_sent_ud_sm-3.8.0/xx_sent_ud_sm-3.8.0-py3-none-any.whl
python -c "import stanza; stanza.download('sr')"
```

### 5️⃣ Run analysis

For a Danish document:

```
python -m src.analyze examples\danish.docx
```

For a Serbian document:

```
python -m src.analyze examples\serbian.docx
```

### 6️⃣ (Optional) Save results

Results are automatically saved to:

```
outputs\<filename>_analysis.txt
```

---

## ⚙️ Common Windows Issues

| Issue                                | Fix                                                                                       |
| ------------------------------------ | ----------------------------------------------------------------------------------------- |
| error: Microsoft Visual C++ required | Install Build Tools from Microsoft                                                        |
| venv\Scripts\activate not found      | Use full path: C:\Users<User>\AppData\Local\Programs\Python\Python311\python -m venv venv |
| Encoding issues (ć, č, ž)            | Run `chcp 65001` in PowerShell to switch to UTF-8                                         |
| Long-path errors                     | Enable: `git config --system core.longpaths true` (run as Administrator)                  |

---

## ⚡ Quick Install (One-liner for PowerShell)

```
git clone https://github.com/milosz94/wordscope.git;
cd wordscope;
python -m venv venv;
venv\Scripts\activate;
pip install -r requirements.txt;
python -m spacy download da_core_news_lg;
pip install https://github.com/explosion/spacy-models/releases/download/xx_sent_ud_sm-3.8.0/xx_sent_ud_sm-3.8.0-py3-none-any.whl;
python -c "import stanza; stanza.download('sr')";
python -m src.analyze examples\danish.docx
```

---

# 🧠 Technical Overview

| Component          | Description                                                                       |
| ------------------ | --------------------------------------------------------------------------------- |
| Language Detection | Uses langdetect to automatically choose between Danish and Serbian                |
| Danish Analysis    | Uses da_core_news_lg spaCy model                                                  |
| Serbian Analysis   | Uses multilingual xx_sent_ud_sm model with fallback to Stanza for higher accuracy |
| Metaphor Detection | Regex rules: “som en”, “ligesom” (Danish) and “kao”, “kao da” (Serbian)           |
| Word Clusters      | Extracted via frequent bigrams                                                    |

---

## 📊 Example Output

```
=== ADJECTIVES ===
ny: 20
ung: 15
stor: 12

=== COMMON WORD CLUSTERS ===
for at: 13
er en: 12

=== POSSIBLE METAPHORS ===
- Goriot er stærk og klar som en klassisk tragedie.
```

---

## 🧱 Project Structure

```
wordscope/
├── README.md
├── requirements.txt
├── setup.sh
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── utils.py
│   └── analyze.py
│
├── examples/
│   ├── danish.docx
│   └── serbian.docx
│
└── outputs/
```

---

## 🧩 License

MIT License © 2025 [Miloš Živanović](./LICENSE

---

## 💡 Future Enhancements

* Generate HTML / Markdown reports with charts
* Add Named Entity Recognition and Dependency Trees
* Support more languages via multilingual transformers
* Optional GUI / web app for drag-and-drop `.docx` analysis

```

