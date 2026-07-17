import re

# Karakter substitusi leet-speak umum untuk menyamarkan kata kotor
LEET_MAP = {
    'a': '[a4@\\*_]',
    'i': '[i1!\\*_]',
    'o': '[o0\\*_]',
    'e': '[e3\\*_]',
    'u': '[u\\*_]',
    's': '[s5$\\*_]',
    'g': '[g9\\*_]',
    't': '[t7\\*_]',
    'b': '[b8\\*_]'
}

def generate_regex_pattern(word: str) -> str:
    """
    Menghasilkan regex pattern untuk satu kata dengan toleransi leet-speak dan sensor.
    Misal: "goblok" -> r"\b[g9\*_][o0\*_]b[l\*_][o0\*_]k\b"
    """
    pattern_parts = []
    for char in word.lower():
        if char in LEET_MAP:
            pattern_parts.append(LEET_MAP[char])
        elif char.isalpha():
            # Setiap huruf alfabet lain secara default bisa digantikan oleh * atau _
            pattern_parts.append(f"[{re.escape(char)}\\*_]")
        else:
            pattern_parts.append(re.escape(char))
    
    # \b untuk word boundary agar tidak match sebagian kata di dalam kata lain yang aman
    return r'\b' + ''.join(pattern_parts) + r'\b'

def compile_toxic_patterns(toxic_words: list[str]) -> list[tuple[re.Pattern, str]]:
    compiled = []
    for word in toxic_words:
        pattern_str = generate_regex_pattern(word)
        try:
            compiled.append((re.compile(pattern_str, re.IGNORECASE), word))
        except re.error as e:
            print(f"Error compiling pattern for {word}: {e}")
    return compiled
