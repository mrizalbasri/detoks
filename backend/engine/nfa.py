import os
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLANG_JSON_PATH = os.path.join(BASE_DIR, 'lexicon', 'slang.json')
GENZ_JSON_PATH = os.path.join(BASE_DIR, 'dataset', 'genz_slang.json')

class NFANormalizer:
    def __init__(self):
        self.slang_map = {}
        self.load_slang_lexicon()

    def load_slang_lexicon(self):
        # 1. Load standard slang lexicon
        if os.path.exists(SLANG_JSON_PATH):
            try:
                with open(SLANG_JSON_PATH, 'r', encoding='utf-8') as f:
                    self.slang_map = json.load(f)
            except Exception as e:
                print(f"Error loading slang.json: {e}")
        else:
            print("slang.json not found, using empty dict")

        # 2. Load and merge Gen Z slang lexicon (preserving existing mappings)
        if os.path.exists(GENZ_JSON_PATH):
            try:
                with open(GENZ_JSON_PATH, 'r', encoding='utf-8') as f:
                    genz_map = json.load(f)
                    for k, v in genz_map.items():
                        if k not in self.slang_map:
                            self.slang_map[k] = v
            except Exception as e:
                print(f"Error loading genz_slang.json: {e}")

    def apply_leet_rules(self, word: str) -> str:
        # Aturan transformasi karakter leet-speak ke huruf normal
        rules = {
            '1': 'i',
            '0': 'o',
            '3': 'e',
            '4': 'a',
            '5': 's',
            '7': 't',
            '8': 'b',
            'z': 's'
        }
        new_word = list(word)
        changed = False
        for i, char in enumerate(new_word):
            if char in rules:
                new_word[i] = rules[char]
                changed = True
        
        return "".join(new_word) if changed else word

    def clean_word(self, word: str) -> tuple[str, str, str]:
        # Memisahkan tanda baca di depan dan belakang kata
        # Mengembalikan (prefix, clean_word, suffix)
        punc = r".,\/#!$%\^&\*;:{}=\-_`~()"
        
        # Cari prefix tanda baca
        prefix_match = re.match(r"^[" + punc + r"]*", word)
        prefix = prefix_match.group(0) if prefix_match else ""
        
        # Cari suffix tanda baca
        suffix_match = re.search(r"[" + punc + r"]*$", word)
        suffix = suffix_match.group(0) if suffix_match else ""
        
        # Potong prefix dan suffix dari word
        clean = word[len(prefix):]
        if suffix:
            clean = clean[:-len(suffix)]
            
        return prefix, clean, suffix

    def normalize(self, text: str) -> tuple[str, list[str]]:
        if not text:
            return "", []

        words = text.split()
        normalized_words = []
        nfa_steps = []

        for word in words:
            # Ubah ke lowercase
            lower_word = word.lower()
            prefix, clean, suffix = self.clean_word(lower_word)
            
            current_word = clean
            
            # 1. Terapkan aturan transformasi leet-speak (pattern-based rules)
            rule_transformed = self.apply_leet_rules(current_word)
            if rule_transformed != current_word:
                nfa_steps.append(f"{current_word} → {rule_transformed} (rule)")
                current_word = rule_transformed

            # 2. Cek ke slang map (dictionary-based)
            if current_word in self.slang_map:
                canonical = self.slang_map[current_word]
                # Hindari duplikasi jika rule sudah mengubahnya ke bentuk baku
                if canonical != current_word:
                    nfa_steps.append(f"{current_word} → {canonical}")
                current_word = canonical
            
            normalized_words.append(prefix + current_word + suffix)

        normalized_text = " ".join(normalized_words)
        return normalized_text, nfa_steps

# Singleton instance
normalizer = NFANormalizer()
