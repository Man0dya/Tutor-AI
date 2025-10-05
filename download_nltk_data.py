"""
NLTK Data Downloader

This script downloads essential NLTK (Natural Language Toolkit) resources
required for the AI Tutoring System. These resources include tokenizers,
stopwords, wordnet, and part-of-speech taggers used for natural language
processing tasks.

Run this script once before using the application to ensure all required
NLTK data is available locally.

Usage:
    Windows: py download_nltk_data.py  OR  python download_nltk_data.py
    macOS/Linux: python3 download_nltk_data.py

Required packages: punkt, punkt_tab, stopwords, wordnet, omw-1.4,
averaged_perceptron_tagger, maxent_ne_chunker, words
"""

import nltk

# List of NLTK packages required for the tutoring system
packages = [
    "punkt",                     # tokenizer
    "punkt_tab",                 # resolves common 'punkt_tab' LookupError on newer NLTK
    "stopwords",
    "wordnet",
    "omw-1.4",                   # optional wordnet language mappings
    "averaged_perceptron_tagger",
    "maxent_ne_chunker",
    "words",
]

print("Starting NLTK downloads...")
for pkg in packages:
    try:
        print(f"→ Downloading: {pkg}")
        nltk.download(pkg, raise_on_error=True)
    except Exception as e:
        print(f"!! Problem downloading {pkg}: {e}")
print("All done. If you saw no errors, you're good to go!")
