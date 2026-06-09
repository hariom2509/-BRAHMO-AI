<div align="center">

# BRAHMO — Derivability Scoring System
### Token Savings Engine · L2 Rules Engine · Check 5

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%2018-61DAFB?style=flat-square&logo=react)](https://react.dev/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python)](https://python.org)
[![Zero LLM](https://img.shields.io/badge/Runtime%20LLM%20Calls-ZERO-brightgreen?style=flat-square)]()

**Classifies 30 healthcare knowledge nodes as DERIVABLE / PARTIALLY_DERIVABLE / NON_DERIVABLE using a hybrid TF-IDF + heuristic algorithm. Zero LLM calls at runtime.**

</div>

---

## What It Does

When a clinician opens an AI session, the Rules Engine injects knowledge nodes into the prompt. Many of these are general medical definitions the LLM already knows — wasted tokens.

BRAHMO scores each node pre-query and excludes the ones the AI can derive itself, saving **~38% of context tokens** per session at no accuracy cost.

**Three classes:**

| Class | Score | Action |
|-------|:-----:|--------|
| 🔴 DERIVABLE | ≥ 0.70 | Excluded from prompt — full tokens saved |
| 🟡 PARTIALLY_DERIVABLE | 0.40–0.69 | Only org-specific delta injected |
| 🟢 NON_DERIVABLE | < 0.40 | Full content always injected |

---

## Scoring Algorithm

**Step 1 — TF-IDF similarity** against a 14-document general medical corpus. High similarity = derivable baseline.

**Step 2 — Heuristic adjustments:**
- Org name "Supra" → −0.40 · Person name → −0.30 · Date reference → −0.20
- Incident reference → −0.30 · Definition structure → +0.20 · Pharmacology terms → +0.15

**Step 3 — Type safety floors** (from `org_config`):
- `CONSTRAINT` max 0.50 · `ANTI_PATTERN` max 0.60 — never fully excluded

**Step 4 — Safety override:** `never_exclude = true` forces score 0.01, bypasses all logic.

---

## Dashboard

![Dashboard — threshold 0.70, 37.9% token savings, Precision 100%, Recall 100%](docs/screenshots/01_dashboard_overview.png)

**Key metrics at default threshold 0.70:**
- Token savings: **37.9%** (683 / 1,802 tokens saved per session)
- Precision: **100%** (target ≥ 85%) · Recall: **100%** (target ≥ 70%)
- Annual savings at 500 engineers: **$12,806/yr**

![Derivable node cards D-03 and D-04 — score 1.00 and 0.97](docs/screenshots/03_derivable_nodes.png)
![Non-derivable ND-01 and ND-02 — score 0.01, full penalty breakdown visible](docs/screenshots/06_non_derivable_nd01_nd02.png)
![Edge case E-01 DVT protocol — CONSTRAINT floor cap applied, 55 tokens saved via delta](docs/screenshots/08_partial_e01_e02_floors.png)

---

## Setup

### Requirements
- Python 3.11+ · Node.js 18+

### Backend
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
Auto-seeds 30 nodes via SQLite. No external DB required.

> **Supabase (optional):** Add `SUPABASE_URL` and `SUPABASE_KEY` to `backend/.env`.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Open **http://localhost:5173**

### Docker (one command)
```bash
docker-compose up --build -d
```
Dashboard at **http://localhost** · API docs at **http://localhost:8000/docs**

### Tests
```bash
cd backend
python -m pytest -v   # 16 tests, all should pass
```

---

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── scorer.py       # Hybrid TF-IDF + heuristic scoring engine
│   │   ├── seed.py         # 30 ground-truth knowledge nodes
│   │   ├── main.py         # FastAPI endpoints
│   │   └── database.py     # Supabase + SQLite dual adapter
│   └── tests/
│       └── test_scorer.py  # 16 unit tests
├── frontend/
│   └── src/App.tsx         # Full dashboard UI
├── docs/
│   ├── architecture.md     # Algorithm design + calibration plan
│   └── screenshots/
├── data_sources.md         # Clinical data provenance
├── docker-compose.yml
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/nodes?org_id=supra` | All 30 scored nodes |
| POST | `/api/rescore?org_id=supra` | Batch rescore all nodes |
| POST | `/api/test-node` | Score a new surprise node |
| POST | `/api/org/{id}/config` | Update threshold + type floors |
| GET | `/api/health` | Health check + DB mode |

---

## Key Design Decisions

- **Hybrid over pure LLM:** Pre-computable, explainable, zero runtime cost, audit-friendly
- **SQLite fallback:** Clone and run instantly — no cloud credentials needed
- **Type floors:** CONSTRAINT nodes can never be fully excluded — safety by design
- **Confidence + Review Queue:** Borderline nodes (0.60–0.80) surfaced for human validation
- **`never_exclude` flag:** Bypasses all scoring for safety-critical nodes (e.g. incident-linked)

See [`docs/architecture.md`](docs/architecture.md) for full algorithm details and calibration plan.  
See [`data_sources.md`](data_sources.md) for clinical data provenance.
