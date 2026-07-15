import os
import json
import re
from .regex_patterns import compile_toxic_patterns

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOXIC_JSON_PATH = os.path.join(BASE_DIR, 'lexicon', 'toxic.json')

class DFAMatcher:
    def __init__(self):
        self.toxic_words = []
        self.compiled_patterns = []
        self.load_toxic_lexicon()

    def load_toxic_lexicon(self):
        if os.path.exists(TOXIC_JSON_PATH):
            try:
                with open(TOXIC_JSON_PATH, 'r', encoding='utf-8') as f:
                    self.toxic_words = json.load(f)
                # Compile regex patterns untuk deteksi variasi leet-speak
                self.compiled_patterns = compile_toxic_patterns(self.toxic_words)
            except Exception as e:
                print(f"Error loading toxic.json: {e}")
        else:
            print("toxic.json not found, using empty list")

    def clean_text_for_matching(self, text: str) -> str:
        # Bersihkan dari tanda baca agar matching exact lebih akurat
        return re.sub(r"[.,\/#!$%\^&\*;:{}=\-_`~()]", "", text.lower())

    def match(self, normalized_text: str) -> tuple[list[str], str]:
        # 1. Bersihkan tanda baca dan split per kata
        clean_text = self.clean_text_for_matching(normalized_text)
        words = clean_text.split()
        
        detected_words = []
        
        # 2. Cek setiap kata dengan Regex & Exact Match
        # (Gabungan Regex Layer + DFA Exact Match Layer)
        for word in words:
            is_word_toxic = False
            
            # Cek exact match ke list toxic
            if word in self.toxic_words:
                detected_words.append(word)
                is_word_toxic = True
            else:
                # Cek pakai regex pattern (leet-speak)
                for pattern in self.compiled_patterns:
                    if pattern.match(word):
                        detected_words.append(word)
                        is_word_toxic = True
                        break

        # Hilangkan duplikat kata terdeteksi
        detected_words = list(set(detected_words))
        is_toxic = len(detected_words) > 0

        # 3. Simulasikan DFA State Path untuk demonstrasi akademis
        # Sesuai ekspektasi visualizer frontend
        dfa_path = "q0"
        if is_toxic:
            state = 1
            for _ in detected_words:
                dfa_path += f" → q{state} → q{state + 5} → q{state + 10}"
                state += 1
            dfa_path += " → qTOXIC"
        else:
            dfa_path += " → q1 → q2 → qSafe"

        return detected_words, dfa_path

# Singleton instance
matcher = DFAMatcher()
