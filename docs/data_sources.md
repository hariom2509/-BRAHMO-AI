# Clinical Data Sources

This document details the original clinical guidelines, research publications, and public health sources where the medical knowledge nodes seeded in **BRAHMO** were sourced.

---

## 1. General Medical Definitions & Pharmacology (DERIVABLE Nodes)

*   **Total Knee Replacement / Arthroplasty (D-01)**
    *   **Source:** NIH National Institute of Arthritis and Musculoskeletal and Skin Diseases (NIAMS) & Mayo Clinic Orthopedics.
    *   **Details:** Standard definitions for joint replacement, surgical methods, and worldwide prevalence metrics.
*   **Paracetamol (Acetaminophen) Mechanism of Action (D-02)**
    *   **Source:** PubChem Database (National Center for Biotechnology Information) & FDA Product Labeling.
    *   **Details:** CNS prostaglandin synthesis inhibition description, typical adult dosing profiles (500mg-1000mg q4-6h), and the 4g daily liver toxicity ceiling.
*   **Normal Adult Vital Sign Ranges (D-03)**
    *   **Source:** American Heart Association (AHA) & Mayo Clinic Clinical Guidelines.
    *   **Details:** Baseline physiologic ranges for heart rate (60-100 bpm), blood pressure (120/80 mmHg), respiratory rate (12-20/min), SpO2 (>95%), and body temperature (36.1-37.2°C).
*   **Deep Vein Thrombosis (DVT) Symptoms & Risks (D-04)**
    *   **Source:** CDC Venous Thromboembolism (VTE) Guidelines & Mayo Clinic.
    *   **Details:** Risk factors associated with post-operative immobility, symptoms (swelling, pain, warmth), and clinical outcomes.
*   **Type 2 Diabetes Mellitus Description (D-05)**
    *   **Source:** American Diabetes Association (ADA) "Standards of Care in Diabetes" & World Health Organization (WHO) Diabetes Fact Sheet.
    *   **Details:** Pathophysiologic profile of peripheral insulin resistance and progressive insulin deficiency.
*   **Warfarin Anticoagulation & INR Targets (D-06)**
    *   **Source:** American College of Cardiology (ACC) & AHA Guidelines on Anticoagulant Therapy.
    *   **Details:** Vitamin K epoxide reductase complex subunit 1 (VKORC1) inhibition, brand naming (Coumadin), and standard therapeutic INR target ranges (2.0-3.0).
*   **Morse Fall Scale Structure (D-07)**
    *   **Source:** Morse, J. M. (1997). *Preventing Patient Falls*. Sage Publications.
    *   **Details:** The six component parameters (history of falling, secondary diagnosis, ambulatory aid, IV/heparin lock, gait, and mental status) and risk scoring (0-125).
*   **SBAR Structured Communication (D-08)**
    *   **Source:** Institute for Healthcare Improvement (IHI) Tools & WHO Patient Safety Solutions.
    *   **Details:** Standardization framework for handover protocols: Situation, Background, Assessment, and Recommendation.
*   **Sepsis SOFA Score Criteria (D-09)**
    *   **Source:** Surviving Sepsis Campaign (SSC) guidelines & Sepsis-3 Consensus (Singer et al., 2016, JAMA).
    *   **Details:** Sequential Organ Failure Assessment (SOFA) scoring thresholds (SOFA ≥2 for organ dysfunction) and septic shock lactate thresholds (>2 mmol/L).
*   **Tramadol Centrally Acting Pharmacology (D-10)**
    *   **Source:** FDA Drug Label (Ultram) & World Health Organization Analgesic Ladder.
    *   **Details:** Dual mechanism of action: weak mu-opioid receptor agonist and monoamine reuptake inhibitor (serotonin and norepinephrine).

---

## 2. Organization-Specific Policies & Operations (NON-DERIVABLE Nodes)

*   **Supra Hospital Pain Management Protocols (ND-01, ND-03, ND-08)**
    *   **Source:** Internal Quality Assurance & Department of Orthopedics clinical guidelines for Supra Multi-Specialty Hospital (Fictionalized/Simulated for the assessment).
    *   **Details:** Preference for Paracetamol 650mg QDS, Zimmer Biomet implants vendor agreement, and FY 2026 local budget parameters (₹4.2 Cr allocation).
*   **Patient Rajan Specific Restrictions (ND-02, ND-04)**
    *   **Source:** Simulated Electronic Health Record (EHR) charts for Patient Rajan.
    *   **Details:** Dual antiplatelet therapy cardiac stent contraindications (2022) and clinical documentation of 8 previous NSAID refusal events.
*   **Supra Sepsis Bundle v3 Update (ND-05)**
    *   **Source:** Supra Hospital Quality Control Board & Infectious Disease Committee (Dr. Meera, June 2026).
    *   **Details:** Local clinical mandates tightening the blood culture and lactate monitoring window down to 1 hour.
*   **Post-Operative Discharge Policy (ND-06)**
    *   **Source:** Supra Medical Safety Board Incident Review Committee (2024 Audit).
    *   **Details:** Local 48-hour safety discharge floor implemented following a DVT readmission case.
*   **Hospital Resource Logistics (ND-07, ND-10)**
    *   **Source:** Supra Operations and Procurement Division.
    *   **Details:** Ward 45 bed layouts (12 surgical, 8 traction, 25 general) and local formulary brand designations (Calpol/Dolo, Omez, Mox, Glycomet).

---

## 3. Ambiguous & Mixed Clinical Guidelines (PARTIALLY_DERIVABLE Nodes)

*   **DVT Prophylaxis Protocol (E-01)**
    *   **General Source:** American College of Chest Physicians (ACCP) Evidence-Based Clinical Practice Guidelines.
    *   **Org-Specific Delta:** Supra Ortho specific Enoxaparin timings (12h post-op) and duration targets (TKR 14d, THR 28d).
*   **Hand Hygiene 5-Moment Compliance (E-02)**
    *   **General Source:** WHO Guidelines on Hand Hygiene in Health Care.
    *   **Org-Specific Delta:** Supra internal NABH compliance targets (95%) and current hospital performance stats (88%).
*   **Fall Risk Morse Scale Implementations (E-03)**
    *   **General Source:** Agency for Healthcare Research and Quality (AHRQ) Fall Prevention Toolkit.
    *   **Org-Specific Delta:** Supra hospital safety threshold of Morse score ≥45 triggering bed alarms and mandatory documentation shift workflows.
*   **Pharmacy Antibiotic Alerts (E-04)**
    *   **General Source:** CDC Core Elements of Hospital Antibiotic Stewardship.
    *   **Org-Specific Delta:** Supra IT pharmacy automation rules pushing de-escalation alerts at 72 hours with automatic escalations to Department HODs.
*   **Double Verification Blood Transfusions (E-05)**
    *   **General Source:** Joint Commission National Patient Safety Goals (NPSG).
    *   **Org-Specific Delta:** Documentation of local near-miss incident in 2024, driving the mandatory two-person nurse verification process.
*   **Supra Emergency Codes (E-06)**
    *   **General Source:** Hospital Association Standardized Emergency Color Codes.
    *   **Org-Specific Delta:** Specific floor-level paging assignments and response team protocols unique to Supra's layout.
*   **Verbal Order Documentation Windows (E-07)**
    *   **General Source:** Joint Commission Rules on Verbal Orders.
    *   **Org-Specific Delta:** Supra strict 1-hour sign-off policy and incident logs from a 2023 medication dosing error.
*   **Elderly Post-Surgical Pain Pathways (E-08)**
    *   **General Source:** American Geriatrics Society (AGS) Clinical Practice Guidelines for Postoperative Pain.
    *   **Org-Specific Delta:** Supra pain ladder steps and safety rule skipping step 2 (Tramadol) for patients over 75 due to fall risks.
*   **Contrast Allergy Pre-Treatment (E-09)**
    *   **General Source:** American College of Radiology (ACR) Contrast Media Manual.
    *   **Org-Specific Delta:** Supra specific IV dosages (Hydrocortisone 200mg + Chlorpheniramine 10mg) and strict 1-hour preparation timings.
*   **Glycemic Sliding Scale Warnings (E-10)**
    *   **General Source:** ADA "Diabetes Care in the Hospital".
    *   **Org-Specific Delta:** Supra historical case audit showing diabetic ketoacidosis (DKA) readmission within 48h, driving mandatory basal insulin inclusion.
