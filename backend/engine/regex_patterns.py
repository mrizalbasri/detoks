import re

# Karakter substitusi leet-speak umum untuk menyamarkan kata kotor
LEET_MAP = {
    'a': '[a4@]',
    'i': '[i1!]',
    'o': '[o0]',
    'e': '[e3]',
    's': '[s5$]',
    'g': '[g9]',
    't': '[t7]',
    'u': '[u]',
    'b': '[b8]'
}

def generate_regex_pattern(word: str) -> str:
    """
    Menghasilkan regex pattern untuk satu kata dengan toleransi leet-speak.
    Misal: "goblok" -> r"\b[g9][o0]bl[o0]k\b"
    """
    pattern_parts = []
    for char in word.lower():
        if char in LEET_MAP:
            pattern_parts.append(LEET_MAP[char])
        else:
            pattern_parts.append(re.escape(char))
    
    # \b untuk word boundary agar tidak match sebagian kata di dalam kata lain yang aman
    return r'\b' + ''.join(pattern_parts) + r'\b'

def compile_toxic_patterns(toxic_words: list[str]) -> list[re.Pattern]:
    compiled = []
    for word in toxic_words:
        pattern_str = generate_regex_pattern(word)
        try:
            compiled.append(re.compile(pattern_str, re.IGNORECASE))
        except re.error as e:
            print(f"Error compiling pattern for {word}: {e}")
    return compiled
