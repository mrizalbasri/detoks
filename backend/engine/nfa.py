import os
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLANG_JSON_PATH = os.path.join(BASE_DIR, 'lexicon', 'slang.json')

class NFANormalizer:
    def __init__(self):
        self.slang_map = {}
        self.load_slang_lexicon()

    def load_slang_lexicon(self):
        if os.path.exists(SLANG_JSON_PATH):
            try:
                with open(SLANG_JSON_PATH, 'r', encoding='utf-8') as f:
                    self.slang_map = json.load(f)
            except Exception as e:
                print(f"Error loading slang.json: {e}")
        else:
            print("slang.json not found, using empty dict")

    def clean_word(self, word: str) -> tuple[str, str]:
        # Memisahkan tanda baca di depan/belakang kata
        # Mengembalikan (clean_word, punctuation_suffix)
        match = re.match(r"^([^.,\/#!$%\^&\*;:{}=\-_`~()]*)(.*)$", word)
        if match:
            return match.group(1), match.group(2)
        return word, ""

    def normalize(self, text: str) -> tuple[str, list[str]]:
        if not text:
            return "", []

        words = text.split()
        normalized_words = []
        nfa_steps = []

        for word in words:
            # Ubah ke lowercase
            lower_word = word.lower()
            clean, suffix = self.clean_word(lower_word)
            
            # Cek ke slang map
            if clean in self.slang_map:
                canonical = self.slang_map[clean]
                nfa_steps.append(f"{clean} → {canonical}")
                normalized_words.append(canonical + suffix)
            else:
                normalized_words.append(clean + suffix)

        normalized_text = " ".join(normalized_words)
        return normalized_text, nfa_steps

# Singleton instance
normalizer = NFANormalizer()
