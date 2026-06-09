# Environment Setup

## Prerequisites
- Python 3.11+
- Node.js 18+

---

## Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Runs on **http://127.0.0.1:8000** — auto-seeds 30 nodes via SQLite on first start. No Supabase needed.

> **Supabase (optional):** Create `backend/.env` with `SUPABASE_URL` and `SUPABASE_KEY`. Falls back to SQLite silently if missing.

---

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

Opens at **http://localhost:5173**

---

## Tests

```powershell
cd backend
python -m pytest -v
```

Expected: **16 passed**

---

## Docker (Production)

```bash
docker-compose up --build -d
```

Dashboard → http://localhost | API Docs → http://localhost:8000/docs

---

## Common Fixes

| Problem | Fix |
|---------|-----|
| venv activation blocked | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Port 8000 in use | `netstat -ano \| findstr :8000` → `taskkill /PID <id> /F` |
| No nodes showing | Click **Reset Seeding** in the dashboard |
| `No module named 'app'` | Run from `backend/` directory with venv active |
