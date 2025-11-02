#!/bin/bash
set -e

echo "📦 Setting up WordScope environment..."

python3 -m venv venv
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🌍 Downloading language models..."
python -m spacy download da_core_news_lg || true

# Multilingual fallback for Serbian
pip install https://github.com/explosion/spacy-models/releases/download/xx_sent_ud_sm-3.8.0/xx_sent_ud_sm-3.8.0-py3-none-any.whl

# Optional: high-accuracy Serbian via Stanza
python -c "import stanza; stanza.download('sr')"

echo "✅ Setup complete!"
echo "Activate with: source venv/bin/activate"
