from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List

from engine.nfa import normalizer
from engine.dfa import matcher

app = FastAPI(
    title="Detox API",
    description="Web-Based Automata Intelligence for Toxic Content Detection",
    version="1.0.0"
)

# CORS configuration to allow local frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Kata-kata sensitif yang tidak boleh ditampilkan di UI frontend
SENSITIVE_WORDS = {"kontol", "memek", "peler", "puki", "jembut", "pussy", "dick"}

def sensor_sensitive_words(words_list: List[str]) -> List[str]:
    """
    Menyensor kata-kata sensitif agar tidak ditampilkan langsung di UI.
    Misal: "kontol" -> "k***ol"
    """
    sensored = []
    for word in words_list:
        if word.lower() in SENSITIVE_WORDS:
            # Sensor dengan menyisakan huruf pertama dan terakhir
            w_len = len(word)
            if w_len > 2:
                sensored.append(word[0] + "*" * (w_len - 2) + word[-1])
            else:
                sensored.append("*" * w_len)
        else:
            sensored.append(word)
    return sensored

# --- Pydantic Schemas ---

class AnalyzeRequest(BaseModel):
    text: str = Field(..., examples=["lo gblk bngst sih"])

class TraceModel(BaseModel):
    nfa_steps: List[str]
    dfa_path: str

class AnalyzeResponse(BaseModel):
    original: str
    normalized: str
    result: str # "TOXIC" | "SAFE"
    detected_words: List[str]
    trace: TraceModel

class BulkAnalyzeRequest(BaseModel):
    texts: List[str] = Field(..., min_items=1)

class BulkItemResponse(BaseModel):
    text: str
    normalized: str
    result: str # "TOXIC" | "SAFE"
    detected_words: List[str]

class BulkAnalyzeResponse(BaseModel):
    total: int
    toxic_count: int
    safe_count: int
    results: List[BulkItemResponse]


# --- Routes ---

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "Detox Automata Engine API is running",
        "lexicon_stats": {
            "slang_count": len(normalizer.slang_map),
            "toxic_count": len(matcher.toxic_words)
        }
    }

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_single(payload: AnalyzeRequest):
    text = payload.text
    if not text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty")
    
    # 1. NFA Normalization Layer
    normalized, nfa_steps = normalizer.normalize(text)
    
    # 2. DFA Matching Layer
    detected_words, dfa_path = matcher.match(normalized)
    
    result_status = "TOXIC" if len(detected_words) > 0 else "SAFE"
    
    # Sensor kata-kata vulgar di daftar kata terdeteksi & hasil normalisasi sebelum dikirim ke frontend
    safe_detected_words = sensor_sensitive_words(detected_words)
    
    # Sensor juga di teks normalisasi agar tidak memunculkan kata vulgar tersebut di UI
    safe_normalized = normalized
    for word in SENSITIVE_WORDS:
        # Cari kata terlarang dalam teks dengan regex (case insensitive)
        pattern = r"\b" + re.escape(word) + r"\b"
        w_len = len(word)
        replacement = word[0] + "*" * (w_len - 2) + word[-1] if w_len > 2 else "*" * w_len
        safe_normalized = re.sub(pattern, replacement, safe_normalized, flags=re.IGNORECASE)
    
    # Sensor langkah NFA trace agar aman di UI
    safe_nfa_steps = []
    for step in nfa_steps:
        temp_step = step
        for word in SENSITIVE_WORDS:
            pattern = r"\b" + re.escape(word) + r"\b"
            w_len = len(word)
            replacement = word[0] + "*" * (w_len - 2) + word[-1] if w_len > 2 else "*" * w_len
            temp_step = re.sub(pattern, replacement, temp_step, flags=re.IGNORECASE)
        safe_nfa_steps.append(temp_step)
        
    return AnalyzeResponse(
        original=text,
        normalized=safe_normalized,
        result=result_status,
        detected_words=safe_detected_words,
        trace=TraceModel(
            nfa_steps=safe_nfa_steps,
            dfa_path=dfa_path
        )
    )

@app.post("/analyze/bulk", response_model=BulkAnalyzeResponse)
def analyze_bulk(payload: BulkAnalyzeRequest):
    valid_texts = [t for t in payload.texts if t.strip()]
    if not valid_texts:
        raise HTTPException(status_code=400, detail="Input list cannot be empty or contain only whitespace")
    
    results = []
    toxic_count = 0
    
    for text in valid_texts:
        # NFA Normalization
        normalized, _ = normalizer.normalize(text)
        # DFA Matching
        detected_words, _ = matcher.match(normalized)
        
        is_toxic = len(detected_words) > 0
        if is_toxic:
            toxic_count += 1
            
        # Sensor untuk hasil bulk
        safe_detected_words = sensor_sensitive_words(detected_words)
        safe_normalized = normalized
        for word in SENSITIVE_WORDS:
            pattern = r"\b" + re.escape(word) + r"\b"
            w_len = len(word)
            replacement = word[0] + "*" * (w_len - 2) + word[-1] if w_len > 2 else "*" * w_len
            safe_normalized = re.sub(pattern, replacement, safe_normalized, flags=re.IGNORECASE)
            
        results.append(BulkItemResponse(
            text=text,
            normalized=safe_normalized,
            result="TOXIC" if is_toxic else "SAFE",
            detected_words=safe_detected_words
        ))
        
    return BulkAnalyzeResponse(
        total=len(valid_texts),
        toxic_count=toxic_count,
        safe_count=len(valid_texts) - toxic_count,
        results=results
    )
