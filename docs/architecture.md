# Architecture & Design Notes: BRAHMO Derivability Scorer

This document outlines the design decisions, mathematical approaches, and validation strategies implemented in the **BRAHMO Derivability Scorer** (Check 5 of the Rules Engine pipeline).

---

## 1. System Philosophy: Safety First

In clinical healthcare systems, AI context safety is a hard constraint. If an AI assistant misses critical organization-specific clinical protocols (e.g., patient-specific allergies, surgical guidelines, or discharge restrictions) because they were filtered out of the prompt context, the results can be catastrophic.

Consequently, the core philosophy of this system is:
> **A False Positive (excluding organization-specific knowledge by misclassifying it as DERIVABLE) is a critical safety failure. A False Negative (including general knowledge by misclassifying it as NON_DERIVABLE) is merely a minor token inefficiency.**

Our algorithm is heavily weighted to default to inclusion (`NON_DERIVABLE` or `PARTIALLY_DERIVABLE`) whenever there is any linguistic signal indicating local customization, patient identifiers, or historical records.

### Safety Safeguards Added:
1. **Manual Override System (`never_exclude`):** Allows forcing a node's score to `0.01` (`NON_DERIVABLE`), ensuring it is always injected into the prompt.
2. **Confidence Score (`HIGH`, `MEDIUM`, `LOW`):** Evaluates the confidence of the classification. Borderline cases are flagged as `LOW` and routed to verification.
3. **Clinician Review Queue:** A UI safety module listing low-confidence and borderline nodes for manual clinician verification.

---

## 2. Core Scoring Algorithm (Hybrid Model)

To avoid query-time LLM latency, the system uses a **Hybrid Scoring Engine** combining statistical term-similarity matching and rule-based heuristics. It is pre-computed at creation/update time or run in background batches.

```
       [Knowledge Node Content]
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
 [never_exclude]     [normal pipeline]
   Override? (Yes)         (No)
        │                   │
        │                   ▼
        │            [TF-IDF Cosine] & [Heuristics]
        │                   │
        │                   ▼
        │            [Combined Score]
        │                   │
        │                   ▼
        │            [Type Floor Check]
        │                   │
        ▼                   ▼
     [Score = 0.01]    [Final Score]
     [Non-Derivable]        │
     [Conf: Override]       ▼
        │            [Confidence Check]
        │            - LOW if borderline (+/-0.10 threshold)
        │            - HIGH if clear signal
        │            - MEDIUM otherwise
        └─────────┬─────────┘
                  ▼
         [Classification Result]
       ┌───────────┼───────────┐
       ▼           ▼           ▼
   [>= 0.70]   [0.40-0.69]  [< 0.40]
   Derivable     Partial    Non-Deriv
   (Exclude)     (Delta)    (Full Link)
```

### Step 2.1: TF-IDF Similarity Check (General Knowledge)
The scorer tokenizes the node content and maps its TF-IDF vector against a reference corpus representing general textbook medical knowledge (e.g., standard definitions of TKR, Sepsis, Paracetamol, WHO guidelines). 
*   We calculate the maximum Cosine Similarity ($S_{max}$) against all documents in the reference corpus.
*   **Base Score Mapping:**
    *   $S_{max} > 0.40 \implies \text{Base} = 0.85 + (S_{max} - 0.40) \times 0.25$
    *   $S_{max} \in (0.20, 0.40] \implies \text{Base} = 0.64 + (S_{max} - 0.20) \times 1.15$
    *   $S_{max} \le 0.20 \implies \text{Base} = 0.25$

### Step 2.2: Heuristic Adjustment
We apply a set of linguistic modifiers to correct the base score based on specific contextual markers:
*   **Penalties (Org-Specific Signals):**
    *   **Org Name ("Supra"):** $-0.40$ (Highly indicative of custom policy).
    *   **Person/Patient Reference ("Dr.", "Mrs.", "Mr.", specific names):** $-0.30$ (Patient logs/doctor decisions are strictly local).
    *   **Specific Date References (years/months/quarters):** $-0.20$ (Indicative of clinical audits/policies).
    *   **Local Logistics & Budget Units ("₹", "Cr", "implants", "beds", "refusals"):** $-0.20$ (Financial/logistical metadata).
    *   **Historical Incidents ("incident [date]", "near-miss", "readmitted"):** $-0.30$ (Clinical risk events).
    *   **Hospital Policies ("policy", "protocol", "threshold" + Org name):** $-0.15$.
    *   **Patient Logs ("nurse documents", "keeps requesting", "family needs"):** $-0.20$.
    *   **Refusal/History Logs ("refused [X] times", "cardiac stent", "dual antiplatelet"):** $-0.20$.
*   **Bonuses (Textbook & Definitional Signals):**
    *   **Definitional Structure (starts with "What is", "X is a", "SBAR is", etc.):** $+0.20$ (Very likely generic definitions).
    *   **Clinical Jargon Density (standard terms like "mechanism", "pharmacology" without Org names):** $+0.15$.

### Step 2.3: Type Safety Floor Caps (Patent Claim 2)
The organization config sets safety ceilings (caps) based on the semantic type of the node. Even if a node has high general similarity and no penalties, we cap the score if its type carries clinical risk:
*   `CONSTRAINT`: capped at `0.50` maximum. (Always included, using at least the delta portion).
*   `ANTI_PATTERN`: capped at `0.60` maximum. (Always included, using at least the delta portion).
*   `DECISION` & `FACT`: no safety floor caps.

### Step 2.4: Classification & Delta Extraction
1.  **DERIVABLE (Score $\ge 0.70$):** Excluded entirely.
2.  **PARTIALLY_DERIVABLE (Score $0.40 \le S < 0.70$):** We include the `non_derivable_portion` only, saving tokens on the surrounding general description.
    *   **Delta Extraction Algorithm:** The engine splits the content into sentences, scans each sentence for any non-derivable keywords (names, dates, numbers, local policies), and filters out the general textbook sentences. Only sentences with specific local indicators are retained as the `non_derivable_portion`.
3.  **NON_DERIVABLE (Score $< 0.40$):** Full content is injected.

### Step 2.5: Confidence & Safety Safeguard Checks
Each node is processed to evaluate the confidence level of the automated algorithm:
*   **Safety-Critical Override (`never_exclude`):** If a node is flagged as safety-critical, calculations are bypassed. The score is forced to `0.01` (`NON_DERIVABLE`), and the confidence is tagged as `HIGH (Override)`.
*   **LOW Confidence:** If the final score falls within $\pm 0.10$ around the threshold (e.g., 0.60 to 0.80 for a 0.70 threshold), it is flagged as `LOW` confidence because it represents a borderline case.
*   **HIGH Confidence:**
    *   If classified as `DERIVABLE` and there are **zero** organization-specific penalties applied.
    *   If classified as `NON_DERIVABLE` and strong local keywords (penalties) are matched.
*   **MEDIUM Confidence:** All other standard classifications.

---

## 3. Operational Calibration & Quality Assurance

To ensure system accuracy does not drift as clinical knowledge nodes accumulate, we design the following calibration framework:

1.  **Manual Ground Truth Labeling:**
    *   When clinical staff or doctors create new knowledge nodes, they can optionally label them (`DERIVABLE`, `PARTIALLY_DERIVABLE`, `NON_DERIVABLE`).
    *   Alternatively, medical reviews can label a random sample (e.g., 200 nodes) to establish a "Gold Standard" evaluation dataset.
2.  **Weekly/Monthly Accuracy Audits:**
    *   Run a scheduled calibration pipeline comparing Scorer outputs against the Gold Standard.
    *   Compute **Precision** and **Recall** metrics:
        $$\text{Precision} = \frac{\text{True Positives}}{\text{True Positives} + \text{False Positives}}$$
        $$\text{Recall} = \frac{\text{True Positives}}{\text{True Positives} + \text{False Negatives}}$$
3.  **Threshold Tuning & Alerts:**
    *   If Precision drops below 85% (meaning False Positives are creeping in, risking missing organization-specific knowledge), the system flags an alert.
    *   Administrator action: increase threshold (e.g., from 0.70 to 0.75 or 0.80) to make exclusion more conservative, or review and refine heuristic regular expressions.
4.  **Clinician Review Queue:**
    *   Low-confidence or borderline nodes are routed to a **Clinician Review Queue** in the UI dashboard, allowing medical administrators to audit them before they are fully excluded from LLM prompts.

---

## 4. Limitations & Future Extensions

*   **Vocabulary Drift:** Simple TF-IDF matching is vocabulary-dependent. If clinical staff write general definitions in non-standard terms, similarity will fail.
    *   *Extension:* Transition from local TF-IDF to local semantic vector comparisons (e.g. running a lightweight local embeddings model like `all-MiniLM-L6-v2` or utilizing Supabase `pgvector` to compare node embeddings against a PubMed vector index).
*   **Static Floors:** Different medical wards may require different safety tolerances.
    *   *Extension:* Support department-specific overrides (e.g. Pediatrics might cap safety constraints at 0.30 instead of 0.50).
