# AI Starter Prompt

Paste this as your **first message** to Claude, GPT-4, or Gemini to give it full project context.

---

```
You are helping me with the BRAHMO Derivability Scoring System — a token savings engine for healthcare AI.

## What it does
Classifies 30 knowledge nodes as DERIVABLE / PARTIALLY_DERIVABLE / NON_DERIVABLE.
Derivable nodes are excluded from AI prompts to save tokens.
Zero LLM calls at runtime — scores are pre-computed and stored in the DB.

## Stack
- Backend: Python 3.11, FastAPI, SQLite (Supabase optional)
- Frontend: React 18 + TypeScript + Vite
- Scoring: Custom TF-IDF + 8 heuristic regex rules

## Scoring Algorithm
1. TF-IDF cosine similarity against 14 general medical documents (corpus)
2. Heuristic penalties: org name −0.40, person name −0.30, dates −0.20, incidents −0.30
3. Heuristic bonuses: definition structure +0.20, pharmacology terms +0.15
4. Type floor caps: CONSTRAINT max 0.50, ANTI_PATTERN max 0.60
5. never_exclude = True → force score 0.01, class NON_DERIVABLE

## Key Files
- scorer.py     → scoring engine (TF-IDF + heuristics)
- seed.py       → 30 nodes with ground truth labels
- main.py       → FastAPI endpoints
- database.py   → Supabase + SQLite dual adapter
- App.tsx       → full dashboard UI

## Key Endpoints
- GET  /api/nodes?org_id=supra    → all scored nodes
- POST /api/rescore?org_id=supra  → batch rescore
- POST /api/test-node             → score a surprise node
- POST /api/org/{id}/config       → update threshold + type floors

## Ground Truth
- D-01…D-10  → DERIVABLE (general medical definitions, score ≥ 0.70)
- ND-01…ND-10 → NON_DERIVABLE (org/patient specific, score < 0.30)
- E-01…E-10  → PARTIALLY_DERIVABLE (mixed, score 0.30–0.70)

## Current Status
- 16/16 tests passing
- Precision: 100%, Recall: 100%
- Token savings: 37.9% at threshold 0.70

What do you need help with?
```
