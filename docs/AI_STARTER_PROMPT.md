# 🤖 AI Starter Prompt
### Use this to onboard any AI assistant (Claude, GPT-4, Gemini) to the BRAHMO codebase instantly

---

## How to Use

Copy the entire block below and paste it as your **first message** to any AI assistant. It gives the AI full context about the project — architecture, constraints, key files, and what the system does — so you can immediately ask technical questions, request features, or debug issues.

---

## The Prompt

```
You are a senior full-stack engineer helping me with the BRAHMO Derivability Scoring System.

## What This System Does

BRAHMO is a token savings engine for healthcare AI. It determines which knowledge nodes in a 
clinical Rules Engine can be safely EXCLUDED from the AI prompt because the LLM already knows 
the content from its training data.

Every knowledge node is classified as:
- DERIVABLE (score ≥ 0.70) → excluded entirely from the prompt → tokens saved
- PARTIALLY_DERIVABLE (0.40–0.69) → only the org-specific delta is injected → partial savings
- NON_DERIVABLE (score < 0.40) → full content always injected → essential context

CRITICAL CONSTRAINT: Zero LLM calls at runtime. Scores are pre-computed and stored in 
the database. At query time, the Rules Engine reads a single column value. Sub-millisecond.

---

## Tech Stack

- Backend: Python 3.11, FastAPI, Uvicorn
- Database: Supabase (PostgreSQL) with automatic SQLite fallback
- Frontend: React 18, TypeScript, Vite, TailwindCSS
- Scoring: Custom TF-IDF + regex heuristics (no ML framework at inference time)
- Tests: pytest (16 tests)
- Deployment: Docker Compose (Nginx + FastAPI)

---

## Scoring Algorithm (Hybrid: TF-IDF + Heuristics)

### Step 1 — TF-IDF Cosine Similarity
A local reference corpus of 14 general medical knowledge documents is pre-built at startup.
Node content is tokenized → TF-IDF vector computed → cosine similarity found against corpus.

Score mapping:
- Similarity > 0.40  → base = 0.85 + (sim - 0.40) × 0.25
- Similarity 0.20–0.40 → base = 0.64 + (sim - 0.20) × 1.15
- Similarity ≤ 0.20   → base = 0.25

### Step 2 — Heuristic Adjustments
8 regex-based signals adjust the TF-IDF base score:
- Org name "Supra" detected → −0.40
- Person/patient name detected → −0.30
- Specific date/year/quarter → −0.20
- Local logistics (beds, budget, refusals) → −0.20
- Incident reference ("incident 2024") → −0.30
- Org policy combined signal → −0.15
- Patient documentation style → −0.20
- Clinical refusal history → −0.20
- Definitional structure ("X is a...") → +0.20 bonus
- Standard pharmacology terms → +0.15 bonus

### Step 3 — Type Safety Floor Caps
Applied from org_config.type_floors:
- CONSTRAINT: max score 0.50 (never fully excluded)
- ANTI_PATTERN: max score 0.60 (never fully excluded)
- DECISION: max 1.0 (no cap)
- FACT: max 1.0 (no cap)

### Step 4 — Confidence Classification
- Score far from threshold with strong signals → HIGH
- Score within ±0.10 of threshold → LOW (routed to Clinician Review Queue)
- Everything else → MEDIUM
- never_exclude = True → HIGH (Override), score forced to 0.01

---

## Key Files

backend/app/scorer.py
  - build_tfidf_model(): builds corpus vectors at startup
  - compute_cosine_similarity(): sparse vector dot product
  - extract_non_derivable_portion(): splits content into derivable/non-derivable sentences
  - score_node(content, node_type, org_name, org_config, never_exclude): main entry point
    Returns: derivability_score, derivability_class, scoring_reason, confidence, 
             type_floor_applied, never_exclude, non_derivable_portion

backend/app/database.py
  - DatabaseAdapter class with dual Supabase/SQLite support
  - Methods: get_organization, update_organization_config, get_nodes, get_node,
             upsert_node, update_node_scores, clear_all, insert_organization
  - SQLite auto-migration: adds never_exclude and confidence columns if missing

backend/app/seed.py
  - 30 nodes: D-01…D-10 (derivable), ND-01…ND-10 (non-derivable), E-01…E-10 (edge cases)
  - Each node has: id, title, content, type, department, tokens_full, tokens_delta,
                   expected_derivability, expected_score_range, non_derivable_portion
  - Seeds org "supra" with default config: threshold=0.70, type_floors as above

backend/app/main.py
  - GET  /api/health
  - GET  /api/org/{org_id}
  - POST /api/org/{org_id}/config (updates threshold + type_floors)
  - GET  /api/nodes?org_id=supra
  - POST /api/rescore?org_id=supra (batch rescore all nodes)
  - POST /api/test-node (score a new node without saving)
  - POST /api/seed (wipe + re-seed)

frontend/src/App.tsx
  - Single-page dashboard (~988 lines)
  - State: nodes[], org{}, threshold, surpriseNeverExclude, expandedNodes{}
  - Computes: tokenStats, savingsPercentage, annualSavings, validationMatrix (TP/FP/TN/FN)
  - Clinician Review Queue: nodes scoring 0.60–0.80 or confidence=LOW
  - Threshold slider: on release → saves config → rescores → recalculates everything

---

## Data Schema (SQLite/Supabase)

organizations table:
  id TEXT PRIMARY KEY
  name TEXT
  config TEXT (JSON: { derivability_threshold, type_floors })

knowledge_nodes table:
  id TEXT PRIMARY KEY
  org_id TEXT
  type TEXT (CONSTRAINT | DECISION | ANTI_PATTERN | FACT)
  title TEXT
  content TEXT
  importance DECIMAL(3,2)
  derivability_score DECIMAL(3,2)
  derivability_class TEXT (DERIVABLE | PARTIALLY_DERIVABLE | NON_DERIVABLE | UNKNOWN)
  non_derivable_portion TEXT
  expected_derivability TEXT
  expected_score_range TEXT
  department TEXT
  tokens_full INTEGER
  tokens_delta INTEGER
  scoring_reason TEXT
  type_floor_applied BOOLEAN
  never_exclude BOOLEAN
  confidence TEXT (HIGH | MEDIUM | LOW | HIGH (Override))
  created_at TEXT

---

## Ground Truth Labels (Assessment Specification)

D-01 to D-10: All FACT type general medical definitions (TKR, Paracetamol, Vital Signs, DVT, 
              Type 2 Diabetes, Warfarin, Morse Fall Scale, SBAR, Sepsis, Tramadol)
              → All should score ≥ 0.70

ND-01 to ND-10: Org-specific hospital decisions, patient records, vendor preferences
               (Supra Paracetamol protocol, Patient Rajan NSAID ban, Zimmer Biomet vendor, etc.)
               → All should score < 0.30

E-01 to E-10: Edge cases (DVT protocol, Hand hygiene, Fall risk, Antibiotic review,
              Blood transfusion verification*, Emergency codes, Verbal orders, Pain escalation,
              Sepsis pathway, Allergy documentation)
              → Should score 0.30–0.70; *E-05 has never_exclude=True

---

## Key Engineering Decisions

1. Hybrid over pure-LLM: Pre-computable, explainable, zero runtime cost, audit-friendly
2. SQLite fallback: Reviewer can clone and run immediately without cloud credentials
3. Type floors over hard rules: Config-driven, org-tunable, doesn't require code changes
4. never_exclude flag: Safety-critical bypass that survives any threshold change
5. Confidence + Review Queue: Borderline cases surfaced for human validation, not auto-decided
6. Sentence-level delta extraction: Splits content at sentence boundaries, tags each sentence 
   by derivability signals to extract only the org-specific portion for PARTIAL nodes

---

## What Works

- All 30 nodes correctly classified at default threshold 0.70
- Tests: 16/16 passing
- Validation matrix: Precision 100%, Recall 100%
- Token savings: 37.9% at threshold 0.70 (~683 tokens / 1,802 total)
- Cost saved: $0.0102/session → $12,806/yr at 500 engineers
- Docker Compose: Working (Nginx + FastAPI)
- Surprise node test: Patient Ramaiah nurse note → score < 0.15, NON_DERIVABLE

---

Now you have full context. What do you need help with?
```

---

## Quick Reference — What to Ask After Pasting

Once the AI has context, here are useful follow-up prompts:

### Debugging
```
The /api/rescore endpoint is returning 500. Here's the traceback: [paste error]
```

### Adding New Features
```
I want to add a department-level threshold override to org_config so different 
departments can have different thresholds. Where should I implement this?
```

### Understanding Code
```
Explain how the extract_non_derivable_portion function in scorer.py works 
and what its limitations are.
```

### Extending the Corpus
```
I want to add 5 more documents to the REFERENCE_CORPUS in scorer.py for 
general pharmacology content. What format should they be in?
```

### Test Coverage
```
Write a pytest test for a new edge case: a node that contains both a general 
medical definition AND an org-specific numerical threshold.
```

### Architecture Questions
```
If we wanted to replace TF-IDF with a local sentence embedding model 
(all-MiniLM-L6-v2), which functions in scorer.py would need to change?
```

### API Extension
```
I want to add a GET /api/nodes/{node_id} endpoint to fetch a single node 
by ID. Show me the FastAPI route handler.
```

---

## Project File Quick Reference

| What you want | File |
|:---|:---|
| Change scoring logic | `backend/app/scorer.py` |
| Add/edit knowledge nodes | `backend/app/seed.py` |
| Add/edit API endpoints | `backend/app/main.py` |
| Database queries | `backend/app/database.py` |
| Environment config | `backend/app/config.py` |
| Frontend dashboard | `frontend/src/App.tsx` |
| Frontend styles | `frontend/src/index.css` |
| Run tests | `backend/tests/test_scorer.py` |
| Docker setup | `docker-compose.yml` |
| Algorithm design | `docs/architecture.md` |
