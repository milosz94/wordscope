import docx
from itertools import tee
from langdetect import detect

def extract_text(path):
    """Extracts raw text from a .docx file."""
    doc = docx.Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

def bigrams(tokens):
    """Generates consecutive token pairs."""
    a, b = tee(tokens)
    next(b, None)
    return list(zip(a, b))

def detect_language(text):
    """Detects whether the text is Danish or Serbian."""
    try:
        lang = detect(text)
        if lang.startswith("da"):
            return "da_core_news_lg"
        elif lang.startswith("sr"):
            return "xx_sent_ud_sm"  # multilingual fallback for Serbian
    except Exception:
        pass
    return "da_core_news_lg"
