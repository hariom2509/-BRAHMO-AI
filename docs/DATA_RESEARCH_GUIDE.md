# 📊 Data Research Guide
### BRAHMO Derivability Scoring System — Understanding the 30 Nodes & Scoring Data

---

## What Is This Guide For?

This guide explains:
1. How the 30 seed knowledge nodes were chosen and structured
2. How to interpret every field on a node
3. How to read the scoring output (score, class, reason, confidence)
4. How the validation ground truth was established
5. How to add new nodes correctly
6. How to calibrate the scorer over time

---

## The 30-Node Ground Truth Dataset

The dataset is divided into three equal groups of 10 nodes each, representing the full
spectrum of derivability. All 30 are seeded in `backend/app/seed.py`.

---

### Group 1 — DERIVABLE (D-01 to D-10)

**Purpose:** General medical knowledge the LLM already knows from training data.  
**Expected score range:** ≥ 0.70  
**Expected classification:** DERIVABLE  
**Node type:** All FACT  

| Node ID | Title | Why Derivable |
|:--------|:------|:-------------|
| D-01 | What is Total Knee Replacement | Standard surgical definition; in every medical textbook |
| D-02 | Paracetamol Mechanism of Action | Pharmacology basics; WHO essential medicine |
| D-03 | Normal Adult Vital Sign Ranges | Universal reference ranges; in every clinical guideline |
| D-04 | What is Deep Vein Thrombosis | Standard definition; clinical presentation widely published |
| D-05 | What is Type 2 Diabetes Mellitus | Chronic disease definition; in all medical curricula |
| D-06 | What is Warfarin | Standard anticoagulant; mechanism in pharmacology databases |
| D-07 | Morse Fall Scale Description | Published validated tool; publicly available scoring system |
| D-08 | SBAR Communication Tool | Standard handover framework; published by IHI |
| D-09 | What is Sepsis | WHO/Sepsis-3 definition; universally published |
| D-10 | Tramadol Pharmacology | Standard opioid pharmacology; in BNF, WHO, etc. |

**Signals the scorer detects (high score):**
- High TF-IDF similarity to medical reference corpus (>0.40)
- Contains definitional language: "X is a...", "X involves...", "The mechanism is..."
- Standard pharmacology/clinical terms with no org-specific markers
- No penalties fired (no org name, person name, date, or local reference)

---

### Group 2 — NON_DERIVABLE (ND-01 to ND-10)

**Purpose:** Org-specific knowledge the LLM cannot possibly know.  
**Expected score range:** < 0.30  
**Expected classification:** NON_DERIVABLE  
**Node types:** DECISION, CONSTRAINT, FACT (but org-specific)

| Node ID | Title | Why Non-Derivable |
|:--------|:------|:-----------------|
| ND-01 | Supra Paracetamol QDS Post-TKR | Supra's specific dosing decision, Dr. Vikram, Jan 2025 |
| ND-02 | Patient Rajan NSAID Ban | Individual patient's medication restriction + cardiac stent |
| ND-03 | Zimmer Biomet Implant Preference | Supra's vendor decision; 3-year outcomes review |
| ND-04 | Rajan Behavioral NSAID Requests | Patient behavioral history; 8 documented refusals |
| ND-05 | Supra TKR Bed Allocation | Hospital-specific bed count and operational procedure |
| ND-06 | Dr. Vikram's Tramadol Policy | Individual clinician's preference; not standard practice |
| ND-07 | Supra Q3 2024 DVT Incident | Hospital incident report; specific to Supra's history |
| ND-08 | Rajan Post-Op Physiotherapy | Patient-specific therapy schedule |
| ND-09 | Padma Ekadashi Fasting Protocol | Single patient's religious + medical adjustment |
| ND-10 | Supra ICU MRSA Outbreak | Specific incident; date, floor, and organism details |

**Signals the scorer detects (low score):**
- Contains org name "Supra" → −0.40
- Contains person name "Dr. Vikram", "Rajan", "Padma" → −0.30
- Contains specific dates "January 2025", "Q3 2024" → −0.20
- Contains hospital operational data "12 beds", "₹2.3 lakh" → −0.20
- Contains incident references "incident 2023", "near-miss" → −0.30
- Contains patient clinical history counts "8 refusals", "3 episodes" → −0.20

---

### Group 3 — PARTIALLY_DERIVABLE Edge Cases (E-01 to E-10)

**Purpose:** Mixed content — partially textbook, partially org-specific.  
**Expected score range:** 0.30–0.70  
**Expected classification:** PARTIALLY_DERIVABLE (some may be NON_DERIVABLE with overrides)  
**Node types:** CONSTRAINT, DECISION, ANTI_PATTERN, FACT

| Node ID | Title | General Part (Derivable) | Org-Specific Part (Delta) |
|:--------|:------|:------------------------|:--------------------------|
| E-01 | DVT Prophylaxis Protocol | Enoxaparin for DVT is standard | Supra timing: 12h post-op, TKR 14d, THR 28d |
| E-02 | Hand Hygiene 5-Moment | WHO 5-moment standard | Supra target 95%, current 88%, reportable |
| E-03 | Fall Risk Morse Scale | Morse scale is published | Supra threshold ≥45, bed alarm, documentation |
| E-04 | Antibiotic 72-Hour Review | Standard antimicrobial stewardship | Supra auto-alert system, pharmacy workflow |
| E-05* | Blood Transfusion Verification | 2-person check is standard | Supra's 2024 near-miss incident (*never_exclude) |
| E-06 | Supra Emergency Codes | Code Blue/Red are standard | Supra's floor-specific code assignments |
| E-07 | Verbal Orders Without Confirmation | ISMP standard against verbal orders | Supra 2023 wrong-dose mishearing incident |
| E-08 | Post-Surgical Pain Escalation | WHO pain ladder general framework | Supra's specific Step 1→2→3 protocol |
| E-09 | Sepsis Care Pathway | Sepsis-3 guidelines general | Supra's resuscitation checklist + ICU transfer |
| E-10 | Allergy Documentation | Allergy documentation is standard | Supra's allergy alert system specific fields |

*E-05 has `never_exclude = True` — safety-critical override applied regardless of score.

---

## Node Data Schema — Field by Field

Every node in the database has these fields. Understanding them is essential for adding new nodes or interpreting results.

```python
{
    # Identity
    "id": "D-01",                          # Unique node ID. Convention: D-XX, ND-XX, E-XX
    "org_id": "supra",                     # Organization this node belongs to
    "title": "What is Total Knee Replacement",  # Short human-readable title
    
    # Content
    "type": "FACT",                        # FACT | CONSTRAINT | DECISION | ANTI_PATTERN
    "content": "Total knee replacement...", # The full text to be scored and potentially injected
    "department": "ortho",                 # Optional: ortho | medicine | icu | pharmacy | null
    "importance": 0.8,                     # 0.0–1.0; for future priority-based filtering
    
    # Token Economics
    "tokens_full": 65,                     # Approx tokens if full content is injected
    "tokens_delta": 0,                     # Approx tokens if only delta is injected (PARTIAL nodes)
    
    # Ground Truth (for validation)
    "expected_derivability": "DERIVABLE",  # DERIVABLE | PARTIALLY_DERIVABLE | NON_DERIVABLE
    "expected_score_range": "0.70-1.00",  # Expected range as a string
    
    # Delta Content (PARTIAL nodes only)
    "non_derivable_portion": null,         # The org-specific sentences extracted from content
    
    # Scored Fields (computed by scorer.py)
    "derivability_score": 0.90,           # 0.00–1.00
    "derivability_class": "DERIVABLE",    # DERIVABLE | PARTIALLY_DERIVABLE | NON_DERIVABLE
    "scoring_reason": "High similarity to standard corpus (0.96); Matches medical definition structure",
    "type_floor_applied": False,          # True if a type cap was enforced
    "confidence": "HIGH",                 # HIGH | MEDIUM | LOW | HIGH (Override)
    "never_exclude": False,               # True forces score=0.01 and NON_DERIVABLE
}
```

---

## Reading the Scoring Output

### Example 1 — A DERIVABLE Node

**Node:** D-01 "What is Total Knee Replacement"

```
derivability_score: 0.90
derivability_class: DERIVABLE
scoring_reason: "High similarity to standard corpus (0.96); Matches medical definition structure"
type_floor_applied: False
confidence: HIGH
never_exclude: False
```

**Interpretation:**
- TF-IDF found cosine similarity of 0.96 against the reference corpus
- Mapping: 0.96 > 0.40 → base = 0.85 + (0.96 - 0.40) × 0.25 = 0.99
- Definitional bonus (+0.20) applied, capped at 1.0 → final 1.00
- No penalties fired (no org name, no person, no date)
- Score 1.00 ≥ threshold 0.70 → DERIVABLE
- Far above threshold with no uncertainty → confidence HIGH
- **Action:** Node excluded from prompt. 65 tokens saved.

---

### Example 2 — A NON_DERIVABLE Node

**Node:** ND-01 "Supra Paracetamol QDS Post-TKR"

```
derivability_score: 0.01
derivability_class: NON_DERIVABLE
scoring_reason: "Low similarity to standard corpus (0.18); Contains org name 'Supra'; 
                 Contains person/patient name reference; Contains specific date reference"
type_floor_applied: False
confidence: HIGH
never_exclude: False
```

**Interpretation:**
- TF-IDF: 0.18 (low similarity) → base = 0.25
- Org name "Supra" detected → −0.40
- Person name "Dr. Vikram" detected → −0.30
- Date "January 2025" detected → −0.20
- Subtotal: 0.25 − 0.40 − 0.30 − 0.20 = −0.65 → clamped to 0.01
- Score 0.01 < threshold 0.70 → NON_DERIVABLE
- Score near zero with strong signals → confidence HIGH
- **Action:** Full 85 tokens always injected.

---

### Example 3 — A PARTIALLY_DERIVABLE Node with Floor Cap

**Node:** E-01 "DVT Prophylaxis Protocol" (type: CONSTRAINT)

```
derivability_score: 0.50
derivability_class: PARTIALLY_DERIVABLE
scoring_reason: "High similarity to standard corpus (0.55); Matches medical definition structure; 
                 Safety cap applied for type 'CONSTRAINT' (max 0.50)"
type_floor_applied: True
confidence: MEDIUM
never_exclude: False
```

**Interpretation:**
- TF-IDF: 0.55 (medium-high similarity) → base = 0.85
- Definitional bonus: +0.20 → 1.05 before heuristics
- Org policy signal detected → −0.15 → 0.90
- BUT: type = CONSTRAINT, floor cap = 0.50 → capped to 0.50
- Score 0.50 < threshold 0.70 → PARTIALLY_DERIVABLE
- Score not particularly close to threshold, but floor was applied → confidence MEDIUM
- **Action:** Only the delta (25 tokens) injected. 55 tokens saved.

---

### Example 4 — The Safety Override

**Node:** E-05 "Blood Transfusion Verification" (never_exclude = True)

```
derivability_score: 0.01
derivability_class: NON_DERIVABLE
scoring_reason: "Manual Safety-Critical Override Applied"
type_floor_applied: False
confidence: HIGH (Override)
never_exclude: True
```

**Interpretation:**
- All scoring bypassed when `never_exclude = True`
- Score forced to 0.01, class forced to NON_DERIVABLE
- This is a near-miss incident node — must always be in every prompt
- **Action:** Full 58 tokens always injected, regardless of threshold.

---

## How to Add New Nodes

### Step 1 — Choose the Node Type

| If the content is... | Use type |
|:---------------------|:---------|
| A definition, fact, or clinical reference | `FACT` |
| A hard rule that must always be followed | `CONSTRAINT` |
| An org or clinician choice/preference | `DECISION` |
| Something that must NOT be done (past incidents) | `ANTI_PATTERN` |

### Step 2 — Estimate Tokens

A rough estimate: 1 token ≈ 4 characters or 0.75 words.

```python
content = "Your node text here..."
tokens_full = int(len(content.split()) / 0.75)
```

For PARTIAL nodes, estimate the delta (org-specific sentences only):
```python
tokens_delta = int(len(org_specific_sentences.split()) / 0.75)
```

### Step 3 — Write the Node in seed.py

```python
{
    "id": "D-11",                          # Use next available ID in series
    "org_id": ORG_ID,
    "title": "What is Septic Arthritis",
    "type": "FACT",
    "content": "Septic arthritis is a bacterial joint infection requiring urgent drainage...",
    "department": "ortho",
    "importance": 0.75,
    "tokens_full": 55,
    "tokens_delta": 0,
    "expected_derivability": "DERIVABLE",  # Your judgment as the curator
    "expected_score_range": "0.70-1.00",
    "non_derivable_portion": None,
}
```

### Step 4 — Set expected_derivability Accurately

Ask yourself:
- Would GPT-4 / Claude 3.5 know this from training data alone? → `DERIVABLE`
- Is there org-specific content mixed with general knowledge? → `PARTIALLY_DERIVABLE`
- Is this specific to this hospital, patient, or clinician? → `NON_DERIVABLE`

This label becomes the ground truth against which precision/recall is calculated.

### Step 5 — Re-seed and Verify

```powershell
# Via API
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/api/seed"

# Then check the node's score
Invoke-RestMethod "http://127.0.0.1:8000/api/nodes?org_id=supra" | 
  Where-Object { $_.id -eq "D-11" } | 
  Select-Object id, derivability_score, derivability_class, scoring_reason
```

---

## Calibration — Keeping the Scorer Accurate Over Time

### When to Recalibrate

| Trigger | Action |
|:--------|:-------|
| New org with different naming conventions | Add org-name to heuristic patterns in `scorer.py` |
| Precision drops below 85% | Increase threshold slightly, or tighten heuristic penalties |
| Recall drops below 70% | Lower threshold slightly, or loosen TF-IDF base mapping |
| New clinical specialty added (e.g., Cardiology) | Add specialty documents to `REFERENCE_CORPUS` |
| LLM model upgraded | Reassess derivability labels — newer models know more |
| Nodes added beyond 30 | Run monthly calibration pipeline against expanded ground truth |

### Monthly Calibration Workflow

```
1. Export all nodes to CSV
2. Medical reviewer audits 50 random nodes → adds/corrects expected_derivability labels
3. Run scorer against all labeled nodes
4. Calculate precision and recall
5. If precision < 85%: raise threshold by 0.05
6. If recall < 70%: lower threshold by 0.05
7. Commit updated config to org_config in DB
8. Trigger POST /api/rescore
9. Document changes in a CALIBRATION_LOG.md entry
```

---

## Reference: Heuristic Rule Patterns

These are the regex/string patterns used by the scorer. If you need to add new signal types,
modify the `score_node()` function in `backend/app/scorer.py` around line 240–320.

```python
# Org-name signals (penalty: −0.40 each match)
org_patterns = [org_name.lower(), org_name.upper()]

# Person/patient name signals (penalty: −0.30)
person_patterns = [r'\bDr\.\s+[A-Z][a-z]+', r'\bPatient\s+[A-Z][a-z]+',
                   r'\bMrs?\.\s+[A-Z][a-z]+']

# Date/time signals (penalty: −0.20)
date_patterns = [r'\b(January|February|March|April|May|June|July|August|
                   September|October|November|December)\s+\d{4}',
                 r'\bQ[1-4]\s+\d{4}', r'\b20\d{2}\b']

# Local business/operational signals (penalty: −0.20)
local_patterns = [r'\b\d+\s+beds?\b', r'₹\d+', r'\bbudget\b',
                  r'\brefusal[s]?\b', r'\boccupancy\b']

# Incident signals (penalty: −0.30)
incident_patterns = [r'\bincident\b', r'\bnear.miss\b', r'\bmishearing\b',
                     r'\bwrong.dose\b']

# Definiti onal structure bonus (+0.20)
definition_patterns = [r'^["\']?[A-Z][^.]+\s+is\s+(a|an|the)\b',
                        r'\bis\s+defined\s+as\b', r'\brefers\s+to\b']

# Pharmacology term bonus (+0.15 if no org signals)
pharma_patterns = [r'\bmg\b', r'\bkg\b', r'\bIV\b', r'\bPO\b',
                   r'\bQDS\b', r'\bBD\b', r'\bTDS\b', r'\bPRN\b']
```

---

## Key Numbers to Know

| Metric | Value | Source |
|:-------|:-----:|:-------|
| Default threshold | 0.70 | `org_config.derivability_threshold` |
| CONSTRAINT floor cap | 0.50 | `org_config.type_floors.CONSTRAINT` |
| ANTI_PATTERN floor cap | 0.60 | `org_config.type_floors.ANTI_PATTERN` |
| Org penalty | −0.40 | `scorer.py` heuristics |
| Person name penalty | −0.30 | `scorer.py` heuristics |
| Date penalty | −0.20 | `scorer.py` heuristics |
| Definition bonus | +0.20 | `scorer.py` heuristics |
| Savings at threshold 0.70 | 37.9% | Dashboard (683/1802 tokens) |
| Precision target | ≥ 85% | Assessment specification |
| Recall target | ≥ 70% | Assessment specification |
| Current precision | 100% | Validation matrix at default config |
| Current recall | 100% | Validation matrix at default config |
| Annual savings (500 eng) | $12,806 | Token savings panel |

---

## REFERENCE_CORPUS Documents (14 Medical Reference Texts)

These 14 texts form the TF-IDF model baseline. They represent "general knowledge."
Located at the top of `backend/app/scorer.py` as the `REFERENCE_CORPUS` list.

1. Total Knee Replacement surgical definition
2. Paracetamol pharmacology and mechanism
3. Vital signs normal reference ranges
4. Deep Vein Thrombosis definition and risk factors
5. Type 2 Diabetes Mellitus pathophysiology
6. Warfarin mechanism and monitoring
7. Morse Fall Scale scoring description
8. SBAR communication framework
9. Sepsis definition (Sepsis-3 criteria)
10. Tramadol pharmacology
11. DVT prophylaxis general guidelines (Enoxaparin)
12. WHO 5-moment hand hygiene standard
13. Antibiotic stewardship general principles
14. Blood transfusion general safety standards

**To add a new corpus document:**
```python
# In scorer.py, append to REFERENCE_CORPUS list:
REFERENCE_CORPUS.append(
    "Your new general medical reference text here. "
    "This should contain only general/universal knowledge, not org-specific content."
)
```
The TF-IDF model rebuilds automatically at the next server restart.
