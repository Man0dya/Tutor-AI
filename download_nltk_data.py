# download_nltk_data.py
# Run this once to fetch common NLTK resources.
# Usage (from your project folder):
#   Windows: py download_nltk_data.py  OR  python download_nltk_data.py
#   macOS/Linux: python3 download_nltk_data.py

import nltk

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
