# BRAHMO Derivability Scoring System (Token Savings Engine)

This project implements a **Derivability Scoring System** for knowledge nodes in **BRAHMO** (organizational knowledge infrastructure for healthcare). It serves as Check 5 of the Rules Engine pipeline.

The system determines whether a knowledge node is:
1.  **DERIVABLE (Score >= 0.70):** The AI already knows this general medical definition from training data. It is **excluded** from the context injected into the doctor's session, saving valuable tokens.
2.  **PARTIALLY_DERIVABLE (Score 0.40 - 0.69):** The node contains some general knowledge but also org-specific timing or targets. Only the **non-derivable delta portion** is injected.
3.  **NON_DERIVABLE (Score < 0.40):** The node is strictly organization-specific (e.g., patient records, custom hospital procedures). The **full content** is injected.

It operates with **ZERO runtime LLM calls** to prevent prompt latency and keep costs at $0.

---

## 🛠️ Project Structure

```
brahmo-derivability/
├── backend/
│   ├── app/
│   │   ├── config.py           # Configuration & fallback logic
│   │   ├── database.py         # Unified DB client (Supabase + SQLite fallback)
│   │   ├── main.py             # FastAPI Server & Routes
│   │   ├── scorer.py           # Scoring Engine (Heuristics + TF-IDF)
│   │   └── seed.py             # Seeds 30 medical knowledge nodes
│   ├── tests/
│   │   └── test_scorer.py      # Automated Scorer & Type Floor tests
│   ├── requirements.txt        # Backend python packages
│   └── db.sqlite3              # Auto-created SQLite DB (if no Supabase)
├── frontend/
│   ├── src/
│   │   ├── App.tsx             # Interactive dashboard component
│   │   ├── index.css           # Styling with Tailwind & scrollbars
│   │   └── main.tsx            # Mounting entry
│   ├── package.json            # Node packages
│   ├── tailwind.config.js      # Tailwind configurations
│   └── postcss.config.js       # PostCSS config
├── docs/
│   └── architecture.md         # Design notes, formulas, and calibration loop
├── data_sources.md             # Clinical references documentation
└── README.md                   # This instruction file
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js v18+ (tested on v24.16.0)

---

### 1. Backend Setup & Run

The backend uses a unified database driver. By default, it will look for Supabase credentials in a `.env` file. If none are found, it **automatically falls back to a local SQLite database (`db.sqlite3`)** and seeds the 30 nodes on startup, enabling an instant out-of-the-box experience.

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Create a virtual environment and activate it:
    - **Windows (PowerShell):**
      ```powershell
      python -m venv venv
      .\venv\Scripts\Activate.ps1
      ```
    - **macOS/Linux:**
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  *(Optional)* Configure Supabase. If you want to use Supabase instead of the SQLite fallback, create a `.env` file in the `backend` folder:
    ```env
    SUPABASE_URL=https://your-project-id.supabase.co
    SUPABASE_KEY=your-anon-key
    ```
5.  Seed the database manually (if using Supabase or forcing re-seeding):
    ```bash
    python -m app.seed
    ```
6.  Start the FastAPI server:
    ```bash
    python -m uvicorn app.main:app --reload
    ```
    The server will run on `http://127.0.0.1:8000`.

---

### 2. Frontend Setup & Run

1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the Vite dev server:
    ```bash
    npm run dev
    ```
    Open `http://localhost:5173` in your browser to view the interactive dashboard.

---

### 3. Docker Compose Deployment (Recommended for Servers)

To build and deploy both the frontend (served via Nginx) and backend (FastAPI) containers seamlessly using Docker:

1.  Ensure you have Docker and Docker Compose installed on your server or local machine.
2.  Start the services in the background:
    ```bash
    docker-compose up --build -d
    ```
3.  Access the application:
    - **Dashboard (Frontend & API reverse proxied):** Open `http://localhost` (Port 80) in your browser.
    - **Backend API Interactive Docs:** Open `http://localhost:8000/docs` (Port 8000) in your browser.
4.  Stop the services:
    ```bash
    docker-compose down
    ```

---

### 4. Running Automated Tests

A comprehensive unit test suite is included to verify the Scoring Engine formulas, thresholds, and safety floor caps:

1.  Navigate to the `backend` folder:
    ```bash
    cd backend
    ```
2.  Ensure your virtual environment is active, and run `pytest`:
    ```bash
    pytest
    ```

---

## 💎 Features Implemented

*   **Pre-computed Scoring Engine:** Uses a hybrid similarity mapping (local TF-IDF model against a general medical corpus) combined with regular-expression heuristics (org name, person names, dates, metrics, and incident audits).
*   **Safety-Critical Override (`never_exclude`):** An administrative database flag that bypasses the scoring logic entirely for high-risk protocols, forcing score `0.01` and confidence `HIGH (Override)`. Node E-05 (Blood Transfusion verification) is pre-seeded with this override.
*   **Scoring Confidence Classification:** Tags nodes as `HIGH`, `MEDIUM`, or `LOW` confidence depending on score margin and rules matching. Borderline nodes within $\pm0.10$ of the threshold are flagged as `LOW`.
*   **Clinician Review Queue:** Routes all low-confidence and borderline nodes to an audit panel in the dashboard, enabling clinical reviewers to perform direct human validation. Clicking a node in the queue smooth-scrolls and flashes the node card for inspection.
*   **Patent-Aligned Type Floors:** Safety floors are enforced via database configs (CONSTRAINT capped at 0.50, ANTI_PATTERN at 0.60), ensuring safety-critical directives are never excluded.
*   **Token Savings Calculator:** Shows active metrics for total context size, tokens saved, percentage savings, cost saved per session, and projected annual savings at organization scale.
*   **Validation Matrix:** Visualizes a Confusion Matrix (True Positives, True Negatives, False Negatives, and critical False Positives) alongside Precision and Recall metrics compared to ground truth labels.
*   **Dynamic Threshold Adjuster:** Features a real-time threshold slider on the dashboard. Adjusting the threshold updates configs, triggers a batch rescore, and recalculates token savings and validation metrics instantly.
*   **Sentence-Level Delta Extraction:** Automatically parses partially derivable nodes to isolate and extract only the organization-specific sentences, discarding the general text.
*   **Live Surprise Node Tester:** Provides an input form to evaluate surprise inputs in real-time, verifying that patient note formats and clinical refusals score low without hardcoding, and supports testing safety-critical checkboxes.
