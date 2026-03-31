import re
import math
import nltk
import pandas as pd
from nltk.corpus import stopwords

nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("omw-1.4")


class PreProcessor:

    def __init__(self):
        """Initializes the preprocessor"""
        pass

    def preprocess_text(self, data):
        """
        Function for cleaning and pre-processing a single text document.
        Applies metadata removal, lowering, punctuation/number removal,
        tokenization and stopword removal.
        """

        def _text_part(value):
            if value is None: return ""
            if isinstance(value, float) and math.isnan(value): return ""
            if pd.isna(value): return ""
            return str(value)

        if isinstance(data, str):
            text = data
        elif hasattr(data, "title") or hasattr(data, "text"):
            _title = _text_part(getattr(data, "title", None))
            _text = _text_part(getattr(data, "text", None))
            text = f"{_title} {_text}".strip()
        elif hasattr(data, "combined_text"):
            text = data.combined_text.strip()

        def sanitize_text(text):
            text = re.sub(r"--.*", "", text, flags=re.DOTALL) # Remove signatures (starting with '-- ')
            text = re.sub(r">.*", "", text) # Remove quote lines (starting with '>')
            text = re.sub(r"\S*@\S*\s?", "", text) # Remove emails
            text = re.sub(r"\s+", " ", text).strip() # Remove line breaks and tabs
            text = text.lower()    
            return text

        text = sanitize_text(text)

        tokens = text.split()

        stop_words = set(stopwords.words("english"))

        clean_tokens = [
            token
            for token in tokens
            if token not in stop_words
            and len(token) > 2  # Remove stopwords and tokens that are too short
        ]

        return " ".join(clean_tokens)