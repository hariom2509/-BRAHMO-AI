# Data Research Guide

## The 30 Nodes — Quick Reference

### D-01 to D-10 — DERIVABLE (score ≥ 0.70)
General medical definitions the LLM already knows. All `FACT` type.

| ID | Title |
|----|-------|
| D-01 | What is Total Knee Replacement |
| D-02 | Paracetamol Mechanism of Action |
| D-03 | Normal Adult Vital Sign Ranges |
| D-04 | What is Deep Vein Thrombosis |
| D-05 | What is Type 2 Diabetes Mellitus |
| D-06 | What is Warfarin |
| D-07 | Morse Fall Scale Description |
| D-08 | SBAR Communication Tool |
| D-09 | What is Sepsis |
| D-10 | Tramadol Pharmacology |

---

### ND-01 to ND-10 — NON_DERIVABLE (score < 0.30)
Hospital/patient-specific content. Mix of DECISION, CONSTRAINT, FACT types.

| ID | Title | Why Non-Derivable |
|----|-------|-------------------|
| ND-01 | Supra Paracetamol QDS Post-TKR | Org protocol, Dr. Vikram, Jan 2025 |
| ND-02 | Patient Rajan NSAID Ban | Patient-specific cardiac contraindication |
| ND-03 | Zimmer Biomet Implant Preference | Supra vendor decision |
| ND-04 | Rajan Behavioral NSAID Requests | 8 documented patient refusals |
| ND-05 | Supra TKR Bed Allocation | Hospital operational data |
| ND-06 | Dr. Vikram's Tramadol Policy | Clinician-specific preference |
| ND-07 | Supra Q3 2024 DVT Incident | Hospital incident report |
| ND-08 | Rajan Post-Op Physiotherapy | Patient-specific schedule |
| ND-09 | Padma Ekadashi Fasting Protocol | Single patient religious adjustment |
| ND-10 | Supra ICU MRSA Outbreak | Specific incident with date + floor |

---

### E-01 to E-10 — PARTIALLY_DERIVABLE (score 0.30–0.70)
Mixed: general knowledge + org-specific protocol. Only the delta is injected.

| ID | Title | Delta (org-specific portion) |
|----|-------|------------------------------|
| E-01 | DVT Prophylaxis Protocol | Supra timing: 12h post-op, TKR 14d |
| E-02 | Hand Hygiene 5-Moment | Supra target 95%, current 88% |
| E-03 | Fall Risk Morse Scale | Supra: score ≥45 = bed alarm |
| E-04 | Antibiotic 72-Hour Review | Supra auto-alert + pharmacy flow |
| E-05* | Blood Transfusion Verification | *never_exclude — 2024 near-miss |
| E-06 | Supra Emergency Codes | Floor-specific code assignments |
| E-07 | Verbal Orders Without Confirmation | Supra 2023 wrong-dose incident |
| E-08 | Post-Surgical Pain Escalation | Supra Step 1→2→3 protocol |
| E-09 | Sepsis Care Pathway | Supra resuscitation checklist |
| E-10 | Allergy Documentation | Supra allergy alert system fields |

*E-05 has `never_exclude = True` — safety override, always injected.

---

## Scoring Signals At a Glance

| Signal | Effect |
|--------|--------|
| Org name "Supra" | −0.40 |
| Person name (Dr./Patient/Mrs.) | −0.30 |
| Specific date or quarter | −0.20 |
| Local ops (beds, budget, refusals) | −0.20 |
| Incident reference | −0.30 |
| Definition structure ("X is a…") | +0.20 |
| Pharmacology terms (mg, QDS, IV) | +0.15 |
| CONSTRAINT type floor cap | max 0.50 |
| ANTI_PATTERN type floor cap | max 0.60 |

---

## Adding a New Node

1. Decide type: `FACT` / `CONSTRAINT` / `DECISION` / `ANTI_PATTERN`
2. Set `expected_derivability` honestly — this is your ground truth
3. Add to `seed.py` following the same dict structure as existing nodes
4. Run `POST /api/seed` or click **Reset Seeding** to reload
5. Check the score in the dashboard — verify it matches your expectation
