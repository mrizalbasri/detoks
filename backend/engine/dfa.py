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
        # Bersihkan dari tanda baca kecuali yang digunakan sebagai substitusi leet/sensor (*, _, @, $, !)
        return re.sub(r"[.,\/#%\^&\*;:{}=\-`~()]", "", text.lower())

    def match(self, normalized_text: str) -> tuple[list[str], str, str]:
        # 1. Bersihkan tanda baca dan split per kata
        # Tetapi kita juga ingin mengganti kata-kata yang tidak baku (seperti b@ngs@t atau g*bl*k)
        # menjadi kata bakunya di dalam teks asli hasil normalisasi.
        
        words = normalized_text.split()
        detected_words = []
        cleaned_words = []
        
        for raw_word in words:
            # Bersihkan word dari tanda baca untuk matching
            word = self.clean_text_for_matching(raw_word)
            if not word:
                cleaned_words.append(raw_word)
                continue
                
            matched_clean_word = None
            
            # Cek exact match ke list toxic
            if word in self.toxic_words:
                matched_clean_word = word
            else:
                # Cek pakai regex pattern (leet-speak)
                for pattern, original_word in self.compiled_patterns:
                    if pattern.match(word):
                        matched_clean_word = original_word
                        break
            
            if matched_clean_word:
                detected_words.append(matched_clean_word)
                # Kembalikan tanda baca jika ada suffix/prefix di raw_word
                pattern_raw = re.compile(re.escape(word), re.IGNORECASE)
                cleaned_word = pattern_raw.sub(matched_clean_word, raw_word)
                cleaned_words.append(cleaned_word)
            else:
                cleaned_words.append(raw_word)
                
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

        clean_normalized_text = " ".join(cleaned_words)
        return detected_words, dfa_path, clean_normalized_text

# Singleton instance
matcher = DFAMatcher()
