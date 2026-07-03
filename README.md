# Detox ✓

> Web-Based Automata Intelligence for Toxic Content Detection  
> Bersihkan toksikmu

![Detox](https://img.shields.io/badge/Detox-v1.0.0-0891B2?style=flat-square)
![SvelteKit](https://img.shields.io/badge/Frontend-SvelteKit-FF3E00?style=flat-square)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square)

---

## 📋 Deskripsi

Detox adalah sistem moderasi konten berbasis rule engine yang menggunakan tiga layer pemrosesan:

1. **NFA** — Normalisasi slang dan variasi ejaan (`gblk` → `goblok`)
2. **Regex** — Pendefinisian pattern toxic secara formal
3. **DFA** — Eksekusi matching deterministik O(n)

Dikembangkan sebagai project mata kuliah **Formal Language and Automata (FLA)**  
Group Greenflag · President University Pekanbaru · 2026

---

## 🗂️ Struktur Project

```
detox/
├── frontend/                 # SvelteKit
│   ├── src/
│   │   ├── routes/
│   │   │   ├── +page.svelte          # Home / Analyzer
│   │   │   ├── bulk/
│   │   │   │   └── +page.svelte      # Bulk Checker
│   │   │   └── riwayat/
│   │   │       └── +page.svelte      # Riwayat
│   │   ├── lib/
│   │   │   ├── components/
│   │   │   │   ├── Navbar.svelte
│   │   │   │   ├── Footer.svelte
│   │   │   │   ├── ResultPanel.svelte
│   │   │   │   └── StatBar.svelte
│   │   │   └── api.js               # Fetch helper ke backend
│   │   └── app.css                  # Global styles + CSS vars
│   ├── package.json
│   ├── svelte.config.js
│   └── vite.config.js
│
├── backend/                  # FastAPI
│   ├── main.py               # Entry point + routes
│   ├── engine/
│   │   ├── nfa.py            # NFA normalization engine
│   │   ├── regex_patterns.py # Regex pattern definitions
│   │   └── dfa.py            # DFA matching engine
│   ├── lexicon/
│   │   ├── slang.json        # Slang → canonical mapping
│   │   └── toxic.json        # Toxic word patterns
│   └── requirements.txt
│
├── docs/
│   ├── diagrams.md           # Mermaid diagrams
│   └── design.md             # Design system
│
└── README.md
```

---

## 🚀 Cara Setup

### Prerequisites

Pastikan sudah terinstall:
- [Node.js](https://nodejs.org) v18+
- [Python](https://python.org) 3.10+
- npm (sudah include dengan Node.js)

---

### 1. Clone Repository

```bash
git clone https://github.com/username/detox.git
cd detox
```

---

### 2. Setup Backend (FastAPI)

```bash
# Masuk ke folder backend
cd backend

# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Jalankan backend
uvicorn main:app --reload --port 8000
```

Backend berjalan di: `http://localhost:8000`  
API docs: `http://localhost:8000/docs`

---

### 3. Setup Frontend (SvelteKit)

Buka terminal baru:

```bash
# Masuk ke folder frontend
cd frontend

# Install dependencies
npm install

# Jalankan frontend
npm run dev
```

Frontend berjalan di: `http://localhost:5173`

---

### 4. Environment Variables

Buat file `.env` di folder `frontend/`:

```env
VITE_API_URL=http://localhost:8000
```

---

## 📡 API Endpoints

### `POST /analyze`
Analisis satu teks.

**Request:**
```json
{
  "text": "lo gblk bngst sih"
}
```

**Response:**
```json
{
  "original": "lo gblk bngst sih",
  "normalized": "lo goblok bangsat sih",
  "result": "TOXIC",
  "detected_words": ["goblok", "bangsat"],
  "trace": {
    "nfa_steps": ["gblk → goblok", "bngst → bangsat"],
    "dfa_path": "q0 → q1 → q6 → q11 → q12 → q13 → qTOXIC"
  }
}
```

---

### `POST /analyze/bulk`
Analisis banyak teks sekaligus.

**Request:**
```json
{
  "texts": [
    "lo gblk bngst sih",
    "makasih udh bantu gw"
  ]
}
```

**Response:**
```json
{
  "total": 2,
  "toxic_count": 1,
  "safe_count": 1,
  "results": [
    {
      "text": "lo gblk bngst sih",
      "normalized": "lo goblok bangsat sih",
      "result": "TOXIC",
      "detected_words": ["goblok", "bangsat"]
    },
    {
      "text": "makasih udh bantu gw",
      "normalized": "makasih sudah bantu aku",
      "result": "SAFE",
      "detected_words": []
    }
  ]
}
```

---

## 📦 Dependencies

### Frontend
```json
{
  "@sveltejs/kit": "^2.0.0",
  "svelte": "^4.0.0",
  "vite": "^5.0.0"
}
```

### Backend
```
fastapi==0.110.0
uvicorn==0.29.0
python-multipart==0.0.9
pydantic==2.6.0
```

---

## 👥 Tim Pengembang

| Nama | NIM | Role |
|---|---|---|
| Cut Sarah Alisa | 030202400012 | NFA Engine + Slang Lexicon |
| M. Rizal Basri | 030202400001 | Backend API + DFA Engine |
| Wesnita Ruth Angie | 030202400019 | Frontend SvelteKit + UI |

---

## 📄 Lisensi

Project ini dibuat untuk keperluan akademik.  
**President University Pekanbaru · Informasi Teknologi · 2026**

---

*Lecturer: Shella Eldwina Fitri S.T., M.Eng*
