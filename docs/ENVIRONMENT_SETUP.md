# 🛠️ Environment Setup Guide
### BRAHMO Derivability Scoring System — Local & Production Setup

---

## Prerequisites

Before you begin, ensure the following are installed on your machine:

| Tool | Version | Download |
|:-----|:-------:|:---------|
| **Python** | 3.11+ | https://python.org/downloads |
| **Node.js** | 18+ (LTS) | https://nodejs.org |
| **Git** | Any | https://git-scm.com |
| **Docker Desktop** *(optional)* | Latest | https://docker.com/products/docker-desktop |

To verify installations:
```powershell
python --version       # Should show 3.11+
node --version         # Should show v18+
npm --version          # Should show 9+
git --version
```

---

## Option A — Local Development (Recommended for Demo)

### Step 1: Clone the Repository

```powershell
git clone <your-repo-url>
cd "Astroum AI"
```

---

### Step 2: Backend Setup

```powershell
# Navigate to backend
cd backend

# Create a Python virtual environment
python -m venv venv

# Activate the virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# If activation is blocked, run this first:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install all dependencies
pip install -r requirements.txt
```

**Verify dependencies installed:**
```powershell
pip list | findstr "fastapi uvicorn scikit-learn"
```

---

### Step 3: Configure Environment Variables

#### Using SQLite (Zero-Config — Recommended for Demo)

No configuration needed. The backend will automatically:
1. Detect that Supabase credentials are missing
2. Fall back to local SQLite database (`backend/db.sqlite3`)
3. Auto-seed all 30 knowledge nodes on first startup

#### Using Supabase (Optional — Cloud Database)

Create a file at `backend/.env`:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-or-service-key
```

> **Note:** If `.env` exists but credentials are invalid, the system silently falls back to SQLite. There is no crash on misconfiguration.

---

### Step 4: Start the Backend Server

```powershell
# Ensure you are inside backend/ with venv activated
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**Expected output:**
```
Running in SQLite mode. Database path: backend/db.sqlite3
Seeding database with 30 ground truth nodes...
Seeding complete. 30 nodes inserted.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Verify the backend is running:
- API Health: http://127.0.0.1:8000/api/health
- Swagger UI: http://127.0.0.1:8000/docs

---

### Step 5: Frontend Setup

Open a **new terminal window** (keep backend running):

```powershell
# Navigate to frontend
cd frontend

# Install Node dependencies
npm install

# Start the Vite development server
npm run dev
```

**Expected output:**
```
  VITE v5.x.x  ready in 500ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

Open your browser at: **http://localhost:5173**

---

### Step 6: Verify Everything Works

1. ✅ Dashboard loads with 30 knowledge nodes visible
2. ✅ Header shows `DB: Connected`
3. ✅ Token Savings panel shows **37.9% saved**
4. ✅ Validation Matrix shows **Precision: 100%** and **Recall: 100%**
5. ✅ Threshold slider is at **0.70**

If nodes don't appear, click **"Reset Seeding"** in the top-right to re-seed the database.

---

## Option B — Docker (One-Command Production Setup)

### Step 1: Ensure Docker Desktop is running

### Step 2: Build and launch all services

```bash
docker-compose up --build -d
```

This starts:
- **FastAPI backend** (internal port 8000)
- **Nginx frontend server** (public port 80)

### Step 3: Access the application

| Service | URL |
|:--------|:----|
| Dashboard | http://localhost |
| API Health | http://localhost/api/health |
| API Docs | http://localhost:8000/docs |

### Step 4: View logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### Step 5: Stop the services

```bash
docker-compose down
```

---

## Running the Test Suite

```powershell
# From the backend/ directory with venv activated
cd backend
python -m pytest -v
```

**Expected output:**
```
tests/test_scorer.py::test_derivable_nodes_score_high[...] PASSED
tests/test_scorer.py::test_non_derivable_nodes_score_low[...] PASSED
tests/test_scorer.py::test_edge_cases_score_middle_and_respect_floors[...] PASSED
tests/test_scorer.py::test_surprise_node_prediction PASSED
tests/test_scorer.py::test_type_safety_floor_enforcement PASSED
tests/test_scorer.py::test_never_exclude_override PASSED
tests/test_scorer.py::test_confidence_evaluation PASSED

===================== 16 passed in 2.31s =====================
```

All 16 tests must pass before submission.

---

## Resetting / Re-seeding the Database

If you need a clean state:

**Via UI:** Click the **"Reset Seeding"** button in the dashboard header.

**Via API:**
```powershell
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/api/seed"
```

**Via cURL (if available):**
```bash
curl -X POST http://127.0.0.1:8000/api/seed
```

---

## Common Issues & Fixes

| Problem | Cause | Fix |
|:--------|:------|:----|
| `venv\Scripts\Activate.ps1` blocked | PowerShell execution policy | Run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Port 8000 already in use | Another process running | Kill with `netstat -ano \| findstr :8000` → `taskkill /PID <id> /F` |
| Port 5173 already in use | Previous Vite server | Close existing terminal or run `npm run dev -- --port 5174` |
| `ModuleNotFoundError: No module named 'app'` | Wrong directory or venv not active | `cd backend` → `.\venv\Scripts\Activate.ps1` → `python -m uvicorn app.main:app` |
| Frontend shows "Failed to fetch" | Backend not running | Start the backend first (Step 4) |
| Dashboard shows 0 nodes | Empty database | Click "Reset Seeding" in the UI |
| `sklearn` not found | pip install missed | `pip install scikit-learn` |

---

## Environment Files Summary

```
Astroum AI/
├── backend/
│   ├── .env                ← Optional: Supabase credentials
│   ├── db.sqlite3          ← Auto-created: SQLite database
│   └── venv/               ← Python virtual environment
├── frontend/
│   └── node_modules/       ← Auto-created: npm packages
└── docker-compose.yml      ← Docker deployment config
```

> **Note:** `.env` and `db.sqlite3` are in `.gitignore` and will never be committed.
