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
    allow_origins=["*"], # Allow all origins for seamless dev integration
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    
    return AnalyzeResponse(
        original=text,
        normalized=normalized,
        result=result_status,
        detected_words=detected_words,
        trace=TraceModel(
            nfa_steps=nfa_steps,
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
            
        results.append(BulkItemResponse(
            text=text,
            normalized=normalized,
            result="TOXIC" if is_toxic else "SAFE",
            detected_words=detected_words
        ))
        
    return BulkAnalyzeResponse(
        total=len(valid_texts),
        toxic_count=toxic_count,
        safe_count=len(valid_texts) - toxic_count,
        results=results
    )
