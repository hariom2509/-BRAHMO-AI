from app.database import db
from app.scorer import score_node

# Organization configurations
ORG_ID = "supra"
ORG_NAME = "Supra Multi-Specialty Hospital"
ORG_CONFIG = {
    "derivability_threshold": 0.7,
    "type_floors": {
        "CONSTRAINT": 0.50,
        "ANTI_PATTERN": 0.60,
        "DECISION": 1.0,
        "FACT": 1.0
    }
}

# 30 Seed Nodes
SEED_NODES = [
    # --- CLEARLY DERIVABLE (10 nodes) ---
    {
        "id": "D-01",
        "org_id": ORG_ID,
        "type": "FACT",
        "title": "What is Total Knee Replacement",
        "content": "Total knee replacement (TKR) is a surgical procedure where damaged knee joint surfaces are replaced with artificial components. Also called total knee arthroplasty (TKA). Most common joint replacement surgery worldwide.",
        "importance": 0.40,
        "expected_derivability": "DERIVABLE",
        "expected_score_range": "0.85-0.95",
        "department": "ortho",
        "tokens_full": 65,
        "tokens_delta": 0,
    },
    {
        "id": "D-02",
        "org_id": ORG_ID,
        "type": "FACT",
        "title": "Paracetamol Mechanism of Action",
        "content": "Paracetamol (acetaminophen) is an analgesic and antipyretic. Mechanism: inhibits prostaglandin synthesis in the CNS. Standard adult dose: 500-1000mg every 4-6 hours, maximum 4g/day.",
        "importance": 0.35,
        "expected_derivability": "DERIVABLE",
        "expected_score_range": "0.90-0.98",
        "department": "medicine",
        "tokens_full": 58,
        "tokens_delta": 0,
    },
    {
        "id": "D-03",
        "org_id": ORG_ID,
        "type": "FACT",
        "title": "Normal Adult Vital Sign Ranges",
        "content": "Normal adult vital signs: HR 60-100 bpm, BP 120/80 mmHg (normal), RR 12-20/min, SpO2 >95%, Temperature 36.1-37.2°C. Variations normal for age, activity, medication.",
        "importance": 0.30,
        "expected_derivability": "DERIVABLE",
        "expected_score_range": "0.92-0.99",
        "department": None,
        "tokens_full": 52,
        "tokens_delta": 0,
    },
    {
        "id": "D-04",
        "org_id": ORG_ID,
        "type": "FACT",
        "title": "What is Deep Vein Thrombosis",
        "content": "Deep vein thrombosis (DVT) is a blood clot in a deep vein, usually in the legs. Risk factors: surgery, immobility, cancer, pregnancy, obesity. Symptoms: leg swelling, pain, warmth, redness.",
        "importance": 0.35,
        "expected_derivability": "DERIVABLE",
        "expected_score_range": "0.88-0.95",
        "department": "ortho",
        "tokens_full": 55,
        "tokens_delta": 0,
    },
    {
        "id": "D-05",
        "org_id": ORG_ID,
        "type": "FACT",
        "title": "What is Type 2 Diabetes Mellitus",
        "content": "Type 2 diabetes mellitus is a chronic condition where the body becomes resistant to insulin or does not produce enough. Most common form of diabetes. Risk factors: obesity, sedentary lifestyle, family history.",
        "importance": 0.30,
        "expected_derivability": "DERIVABLE",
        "expected_score_range": "0.90-0.97",
        "department": "medicine",
        "tokens_full": 50,
        "tokens_delta": 0,
    },
    {
        "id": "D-06",
        "org_id": ORG_ID,
        "type": "FACT",
        "title": "What is Warfarin",
        "content": "Warfarin is an anticoagulant medication that prevents blood clots. Mechanism: inhibits vitamin K-dependent clotting factors. Common brand: Coumadin. Monitored via INR (target usually 2.0-3.0).",
        "importance": 0.35,
        "expected_derivability": "DERIVABLE",
        "expected_score_range": "0.88-0.95",
        "department": None,
        "tokens_full": 52,
        "tokens_delta": 0,
    },
    {
        "id": "D-07",
        "org_id": ORG_ID,
        "type": "FACT",
        "title": "Morse Fall Scale Description",
        "content": "The Morse Fall Scale is a rapid assessment tool for fall risk in hospitalized patients. Six items scored: history of falling, secondary diagnosis, ambulatory aid, IV/heparin lock, gait, mental status. Score 0-125.",
        "importance": 0.40,
        "expected_derivability": "DERIVABLE",
        "expected_score_range": "0.82-0.92",
        "department": None,
        "tokens_full": 58,
        "tokens_delta": 0,
    },
    {
        "id": "D-08",
        "org_id": ORG_ID,
        "type": "FACT",
        "title": "SBAR Communication Tool",
        "content": "SBAR is a structured communication tool: Situation (what is happening), Background (context), Assessment (your assessment), Recommendation (what you think should happen). Used in healthcare handovers.",
        "importance": 0.35,
        "expected_derivability": "DERIVABLE",
        "expected_score_range": "0.85-0.93",
        "department": None,
        "tokens_full": 50,
        "tokens_delta": 0,
    },
    {
        "id": "D-09",
        "org_id": ORG_ID,
        "type": "FACT",
        "title": "What is Sepsis",
        "content": "Sepsis is a life-threatening organ dysfunction caused by dysregulated host response to infection. Criteria: suspected infection + SOFA score ≥2. Septic shock: sepsis + vasopressor requirement + lactate >2.",
        "importance": 0.40,
        "expected_derivability": "DERIVABLE",
        "expected_score_range": "0.85-0.93",
        "department": "medicine",
        "tokens_full": 55,
        "tokens_delta": 0,
    },
    {
        "id": "D-10",
        "org_id": ORG_ID,
        "type": "FACT",
        "title": "Tramadol Pharmacology",
        "content": "Tramadol is a centrally acting synthetic opioid analgesic. Binds to mu-opioid receptors. Also inhibits serotonin and norepinephrine reuptake. Adult dose: 50-100mg q4-6h. Max: 400mg/day.",
        "importance": 0.30,
        "expected_derivability": "DERIVABLE",
        "expected_score_range": "0.88-0.95",
        "department": None,
        "tokens_full": 52,
        "tokens_delta": 0,
    },

    # --- CLEARLY NON-DERIVABLE (10 nodes) ---
    {
        "id": "ND-01",
        "org_id": ORG_ID,
        "type": "DECISION",
        "title": "Supra Paracetamol QDS Post-TKR",
        "content": "Supra Ortho uses Paracetamol 650mg QDS as first-line post-TKR pain management. Escalation: Tramadol 50mg if VAS > 6. AVOID NSAIDs. Decision by Dr. Vikram, January 2025.",
        "importance": 0.88,
        "expected_derivability": "NON_DERIVABLE",
        "expected_score_range": "0.02-0.10",
        "department": "ortho",
        "tokens_full": 85,
        "tokens_delta": 85,
    },
    {
        "id": "ND-02",
        "org_id": ORG_ID,
        "type": "CONSTRAINT",
        "title": "Patient Rajan NSAID Ban",
        "content": "ABSOLUTE CONTRAINDICATION: No ibuprofen, no aspirin, no diclofenac for patient Rajan. Cardiac stent (2022) + dual antiplatelet. Previous 8 NSAID refusals documented. Paracetamol ONLY.",
        "importance": 0.99,
        "expected_derivability": "NON_DERIVABLE",
        "expected_score_range": "0.01-0.05",
        "department": "ortho",
        "tokens_full": 72,
        "tokens_delta": 72,
    },
    {
        "id": "ND-03",
        "org_id": ORG_ID,
        "type": "DECISION",
        "title": "Zimmer Biomet Implant Preference",
        "content": "Supra Ortho Department uses Zimmer Biomet as preferred TKR implant vendor. Alternative: Smith & Nephew for revision cases only. Decision based on 3-year outcomes review, Dr. Vikram, 2024.",
        "importance": 0.72,
        "expected_derivability": "NON_DERIVABLE",
        "expected_score_range": "0.02-0.08",
        "department": "ortho",
        "tokens_full": 68,
        "tokens_delta": 68,
    },
    {
        "id": "ND-04",
        "org_id": ORG_ID,
        "type": "FACT",
        "title": "Rajan Behavioral NSAID Requests",
        "content": "Patient Rajan repeatedly requests Ibuprofen for knee pain despite 8 documented refusals. Family (son) also requests. Counseled each visit. Behavioral note for future visits.",
        "importance": 0.72,
        "expected_derivability": "NON_DERIVABLE",
        "expected_score_range": "0.01-0.05",
        "department": "ortho",
        "tokens_full": 62,
        "tokens_delta": 62,
    },
    {
        "id": "ND-05",
        "org_id": ORG_ID,
        "type": "DECISION",
        "title": "Sepsis Protocol v3 Supra",
        "content": "Supra Sepsis Bundle v3 (2026): blood cultures before antibiotics, lactate within 1 HOUR (tightened from v2 3-hour window). Pip-Tazo empiric. Dr. Meera, updated June 2026.",
        "importance": 0.92,
        "expected_derivability": "NON_DERIVABLE",
        "expected_score_range": "0.05-0.15",
        "department": "medicine",
        "tokens_full": 75,
        "tokens_delta": 75,
    },
    {
        "id": "ND-06",
        "org_id": ORG_ID,
        "type": "ANTI_PATTERN",
        "title": "TKR Discharge Under 48 Hours",
        "content": "Do NOT discharge TKR patients before 48 hours. Past incident: patient discharged at 36 hours developed DVT at home, emergency readmission. Supra policy since 2024.",
        "importance": 0.91,
        "expected_derivability": "NON_DERIVABLE",
        "expected_score_range": "0.05-0.15",
        "department": "ortho",
        "tokens_full": 68,
        "tokens_delta": 68,
    },
    {
        "id": "ND-07",
        "org_id": ORG_ID,
        "type": "FACT",
        "title": "Ortho Ward 45 Beds",
        "content": "Ortho Ward: 45 beds total. 12 post-surgical, 8 traction, 25 general ortho. Usual occupancy 85-90%. Winter peak: 100%+, overflow to Medicine Ward.",
        "importance": 0.50,
        "expected_derivability": "NON_DERIVABLE",
        "expected_score_range": "0.05-0.15",
        "department": "ortho",
        "tokens_full": 55,
        "tokens_delta": 55,
    },
    {
        "id": "ND-08",
        "org_id": ORG_ID,
        "type": "DECISION",
        "title": "Ortho Budget 2026",
        "content": "FY 2026 Ortho budget: ₹4.2 Cr. Implants 45%, Staffing 30%, Equipment 15%, Training 10%. New arthroscopy equipment approved Q3.",
        "importance": 0.70,
        "expected_derivability": "NON_DERIVABLE",
        "expected_score_range": "0.01-0.05",
        "department": "ortho",
        "tokens_full": 58,
        "tokens_delta": 58,
    },
    {
        "id": "ND-09",
        "org_id": ORG_ID,
        "type": "FACT",
        "title": "Padma Ekadashi Fasting",
        "content": "Mrs. Padma (62F, Type 2 DM) observes Ekadashi fasting twice monthly. Skip Glimepiride on fast days. Continue Metformin with evening meal. 3 hypoglycemia episodes before adjustment.",
        "importance": 0.82,
        "expected_derivability": "NON_DERIVABLE",
        "expected_score_range": "0.01-0.05",
        "department": "medicine",
        "tokens_full": 65,
        "tokens_delta": 65,
    },
    {
        "id": "ND-10",
        "org_id": ORG_ID,
        "type": "FACT",
        "title": "Supra Formulary Brands",
        "content": "Supra formulary preferred brands: Paracetamol (Calpol/Dolo), Omeprazole (Omez), Amoxicillin (Mox), Metformin (Glycomet). Use formulary brand unless clinical reason documented.",
        "importance": 0.65,
        "expected_derivability": "NON_DERIVABLE",
        "expected_score_range": "0.08-0.20",
        "department": None,
        "tokens_full": 55,
        "tokens_delta": 55,
    },

    # --- AMBIGUOUS EDGE CASES (10 nodes) ---
    {
        "id": "E-01",
        "org_id": ORG_ID,
        "type": "CONSTRAINT",
        "title": "DVT Prophylaxis Protocol",
        "content": "ALL ortho surgical patients receive DVT prophylaxis: Enoxaparin 40mg SC daily starting 12 hours post-op. Duration: 14 days for TKR, 28 days for THR. Contraindication: active bleeding, platelet <50K.",
        "importance": 0.93,
        "expected_derivability": "PARTIALLY_DERIVABLE",
        "expected_score_range": "0.40-0.60",
        "department": "ortho",
        "tokens_full": 80,
        "tokens_delta": 25,
        "non_derivable_portion": "Supra: Enoxaparin 12 hours post-op. TKR 14d, THR 28d. Active bleeding/platelet <50K contraindicated.",
    },
    {
        "id": "E-02",
        "org_id": ORG_ID,
        "type": "CONSTRAINT",
        "title": "Hand Hygiene 5-Moment Compliance",
        "content": "WHO 5-moment hand hygiene compliance mandatory. Supra target: 95%. Current: 88%. Alcohol-based handrub at every bed. Non-compliance is a reportable incident.",
        "importance": 0.90,
        "expected_derivability": "PARTIALLY_DERIVABLE",
        "expected_score_range": "0.40-0.55",
        "department": None,
        "tokens_full": 55,
        "tokens_delta": 22,
        "non_derivable_portion": "Supra target 95%, current 88%. Handrub at every bed. Non-compliance is reportable incident.",
    },
    {
        "id": "E-03",
        "org_id": ORG_ID,
        "type": "CONSTRAINT",
        "title": "Fall Risk Morse Scale",
        "content": "Every patient assessed for fall risk using Morse Fall Scale on admission and every shift change. Score >= 45: high risk, bed alarm required. Supra threshold and documentation requirements.",
        "importance": 0.85,
        "expected_derivability": "PARTIALLY_DERIVABLE",
        "expected_score_range": "0.45-0.60",
        "department": None,
        "tokens_full": 55,
        "tokens_delta": 20,
        "non_derivable_portion": "Supra: score ≥45 = bed alarm. Assessment on admission + every shift. Documentation required.",
    },
    {
        "id": "E-04",
        "org_id": ORG_ID,
        "type": "DECISION",
        "title": "Antibiotic 72-Hour Review",
        "content": "All empiric antibiotics reviewed at 72 hours. De-escalate based on culture results. Supra policy: pharmacy auto-alerts at 72 hours. Non-compliance flagged to department HOD.",
        "importance": 0.88,
        "expected_derivability": "PARTIALLY_DERIVABLE",
        "expected_score_range": "0.35-0.55",
        "department": None,
        "tokens_full": 60,
        "tokens_delta": 22,
        "non_derivable_portion": "Supra: pharmacy auto-alerts at 72h. Non-compliance flagged to HOD.",
    },
    {
        "id": "E-05",
        "org_id": ORG_ID,
        "type": "CONSTRAINT",
        "title": "Blood Transfusion Verification",
        "content": "ALL blood transfusions require two-person verification of patient identity, blood type, and unit number. Supra incident 2024: near-miss due to single verification.",
        "importance": 0.97,
        "expected_derivability": "PARTIALLY_DERIVABLE",
        "expected_score_range": "0.35-0.50",
        "department": None,
        "tokens_full": 58,
        "tokens_delta": 18,
        "non_derivable_portion": "Supra incident 2024: near-miss single verification. Two-person mandatory.",
        "never_exclude": True,
    },
    {
        "id": "E-06",
        "org_id": ORG_ID,
        "type": "FACT",
        "title": "Supra Emergency Codes",
        "content": "Code Blue: cardiac arrest. Code Red: fire. Code Pink: infant abduction. Code Grey: combative patient. All staff must know codes for their floor.",
        "importance": 0.70,
        "expected_derivability": "PARTIALLY_DERIVABLE",
        "expected_score_range": "0.50-0.65",
        "department": None,
        "tokens_full": 48,
        "tokens_delta": 15,
        "non_derivable_portion": "Supra floor-specific assignments for each code.",
    },
    {
        "id": "E-07",
        "org_id": ORG_ID,
        "type": "ANTI_PATTERN",
        "title": "Verbal Orders Without Confirmation",
        "content": "NEVER accept verbal orders for medication changes without written confirmation within 1 hour. Supra incident 2023: wrong dose from mishearing. Exception: cardiac arrest.",
        "importance": 0.90,
        "expected_derivability": "PARTIALLY_DERIVABLE",
        "expected_score_range": "0.35-0.50",
        "department": None,
        "tokens_full": 55,
        "tokens_delta": 20,
        "non_derivable_portion": "Supra incident 2023: wrong dose mishearing. 1-hour written confirmation mandatory.",
    },
    {
        "id": "E-08",
        "org_id": ORG_ID,
        "type": "DECISION",
        "title": "Post-Surgical Pain Escalation",
        "content": "Pain escalation: Step 1 Paracetamol 650mg QDS → Step 2 Tramadol 50mg TDS → Step 3 Morphine 5mg PRN. Skip Step 2 for elderly >75 (fall risk). Supra protocol.",
        "importance": 0.80,
        "expected_derivability": "PARTIALLY_DERIVABLE",
        "expected_score_range": "0.40-0.55",
        "department": "ortho",
        "tokens_full": 68,
        "tokens_delta": 25,
        "non_derivable_portion": "Supra protocol: skip Tramadol step for elderly >75 (fall risk). QDS/TDS specific timing.",
    },
    {
        "id": "E-09",
        "org_id": ORG_ID,
        "type": "CONSTRAINT",
        "title": "Contrast Allergy Pre-Treatment",
        "content": "Patients with contrast allergy: Hydrocortisone 200mg IV + Chlorpheniramine 10mg IV, 1 hour before procedure. Supra uses this as standard protocol.",
        "importance": 0.88,
        "expected_derivability": "PARTIALLY_DERIVABLE",
        "expected_score_range": "0.45-0.60",
        "department": "medicine",
        "tokens_full": 55,
        "tokens_delta": 18,
        "non_derivable_portion": "Supra standard: Hydrocortisone 200mg + Chlorpheniramine 10mg, 1 hour before.",
    },
    {
        "id": "E-10",
        "org_id": ORG_ID,
        "type": "ANTI_PATTERN",
        "title": "Insulin Sliding Scale Alone",
        "content": "Do NOT use insulin sliding scale as sole glycemic management. Supra past incident: DKA patient readmitted 48 hours. Always include basal insulin. Sliding scale supplements only.",
        "importance": 0.87,
        "expected_derivability": "PARTIALLY_DERIVABLE",
        "expected_score_range": "0.35-0.50",
        "department": "medicine",
        "tokens_full": 58,
        "tokens_delta": 20,
        "non_derivable_portion": "Supra incident: DKA readmission 48h on sliding scale alone. Mandatory basal insulin.",
    }
]

def seed_db():
    """Seed the database with the organization and 30 knowledge nodes."""
    print("Clearing tables...")
    db.clear_all()
    
    print(f"Seeding organization: {ORG_ID}...")
    db.insert_organization(ORG_ID, ORG_NAME, ORG_CONFIG)
    
    print("Seeding nodes...")
    count = 0
    for node in SEED_NODES:
        # Precompute the score using the scorer
        scored_fields = score_node(
            content=node["content"],
            node_type=node["type"],
            org_name="Supra",
            org_config=ORG_CONFIG,
            never_exclude=node.get("never_exclude", False)
        )
        
        # Combine base fields and computed scored fields
        complete_node = {**node}
        
        # Override computed fields from our scorer
        complete_node["derivability_score"] = scored_fields["derivability_score"]
        complete_node["derivability_class"] = scored_fields["derivability_class"]
        complete_node["scoring_reason"] = scored_fields["scoring_reason"]
        complete_node["type_floor_applied"] = scored_fields["type_floor_applied"]
        complete_node["never_exclude"] = scored_fields["never_exclude"]
        complete_node["confidence"] = scored_fields["confidence"]
        
        # For seed data, keep the provided non_derivable_portion and tokens_delta 
        # if the node is PARTIALLY_DERIVABLE, otherwise use the scorer's output
        if scored_fields["derivability_class"] != "PARTIALLY_DERIVABLE":
            complete_node["non_derivable_portion"] = scored_fields["non_derivable_portion"]
            complete_node["tokens_delta"] = scored_fields["tokens_delta"]
        else:
            # Keep manual override for ground truth if it matches E-01 to E-10
            if "non_derivable_portion" not in complete_node or not complete_node["non_derivable_portion"]:
                complete_node["non_derivable_portion"] = scored_fields["non_derivable_portion"]
                complete_node["tokens_delta"] = scored_fields["tokens_delta"]

        db.upsert_node(complete_node)
        count += 1
        
    print(f"Successfully seeded {count} nodes.")

if __name__ == "__main__":
    seed_db()
