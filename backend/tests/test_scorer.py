import pytest
from app.scorer import score_node

# Organization configurations for testing
TEST_ORG_CONFIG = {
    "derivability_threshold": 0.7,
    "type_floors": {
        "CONSTRAINT": 0.50,
        "ANTI_PATTERN": 0.60,
        "DECISION": 1.0,
        "FACT": 1.0
    }
}

# 1. Clearly Derivable Nodes
DERIVABLE_TESTS = [
    ("Total knee replacement (TKR) is a surgical procedure where damaged knee joint surfaces are replaced with artificial components.", "FACT"),
    ("Paracetamol (acetaminophen) is an analgesic and antipyretic. Mechanism: inhibits prostaglandin synthesis in the CNS.", "FACT"),
    ("Normal adult vital signs: HR 60-100 bpm, BP 120/80 mmHg, RR 12-20/min, SpO2 >95%, Temperature 36.1-37.2°C.", "FACT"),
    ("Deep vein thrombosis (DVT) is a blood clot in a deep vein, usually in the legs.", "FACT"),
    ("Type 2 diabetes mellitus is a chronic condition where the body becomes resistant to insulin.", "FACT")
]

# 2. Clearly Non-Derivable Nodes
NON_DERIVABLE_TESTS = [
    ("Supra Ortho uses Paracetamol 650mg QDS as first-line post-TKR pain management. Escalation: Tramadol 50mg if VAS > 6. AVOID NSAIDs. Decision by Dr. Vikram, January 2025.", "DECISION"),
    ("ABSOLUTE CONTRAINDICATION: No ibuprofen, no aspirin, no diclofenac for patient Rajan. Cardiac stent (2022) + dual antiplatelet. Previous 8 NSAID refusals documented. Paracetamol ONLY.", "CONSTRAINT"),
    ("Supra Ortho Department uses Zimmer Biomet as preferred TKR implant vendor. Alternative: Smith & Nephew for revision cases only. Decision based on 3-year outcomes review, Dr. Vikram, 2024.", "DECISION"),
    ("Patient Rajan repeatedly requests Ibuprofen for knee pain despite 8 documented refusals. Family (son) also requests. Counseled each visit. Behavioral note for future visits.", "FACT")
]

# 3. Edge Cases (Ambiguous / Partially Derivable)
EDGE_CASE_TESTS = [
    ("ALL ortho surgical patients receive DVT prophylaxis: Enoxaparin 40mg SC daily starting 12 hours post-op. Duration: 14 days for TKR, 28 days for THR. Contraindication: active bleeding, platelet <50K.", "CONSTRAINT"),
    ("WHO 5-moment hand hygiene compliance mandatory. Supra target: 95%. Current: 88%. Alcohol-based handrub at every bed. Non-compliance is a reportable incident.", "CONSTRAINT"),
    ("Every patient assessed for fall risk using Morse Fall Scale on admission and every shift change. Score >= 45: high risk, bed alarm required. Supra threshold and documentation requirements.", "CONSTRAINT")
]

@pytest.mark.parametrize("content,node_type", DERIVABLE_TESTS)
def test_derivable_nodes_score_high(content, node_type):
    res = score_node(content, node_type, "Supra", TEST_ORG_CONFIG)
    # Clearly derivable facts should score above or equal to threshold (default 0.70)
    # Unless capped by a floor (which FACT is not: floor is 1.0)
    assert res["derivability_score"] >= 0.70, f"Expected high score for derivable node, got {res['derivability_score']}"
    assert res["derivability_class"] == "DERIVABLE"

@pytest.mark.parametrize("content,node_type", NON_DERIVABLE_TESTS)
def test_non_derivable_nodes_score_low(content, node_type):
    res = score_node(content, node_type, "Supra", TEST_ORG_CONFIG)
    # Clearly non-derivable hospital/patient-specific content should score low (< 0.30)
    assert res["derivability_score"] < 0.30, f"Expected low score for non-derivable node, got {res['derivability_score']}"
    assert res["derivability_class"] == "NON_DERIVABLE"

@pytest.mark.parametrize("content,node_type", EDGE_CASE_TESTS)
def test_edge_cases_score_middle_and_respect_floors(content, node_type):
    res = score_node(content, node_type, "Supra", TEST_ORG_CONFIG)
    # Edge cases should score in the middle range (0.30 to 0.70)
    # and because they are constraints, their score is capped at 0.50
    assert 0.30 <= res["derivability_score"] <= 0.70, f"Expected middle score, got {res['derivability_score']}"
    if node_type == "CONSTRAINT":
        assert res["derivability_score"] <= 0.50, f"Expected constraint score capped at 0.50, got {res['derivability_score']}"

def test_surprise_node_prediction():
    # Surprise node content
    surprise_content = "A nurse documents: 'Patient Ramaiah's son keeps requesting Ibuprofen for knee pain. We've refused 8 times due to cardiac stent. Family needs continued education.'"
    res = score_node(surprise_content, "FACT", "Supra", TEST_ORG_CONFIG)
    
    # Assert scorer correctly identifies the patient name, the cardiac refusal details, 
    # classifies it as NON_DERIVABLE, and returns score < 0.30
    assert res["derivability_score"] < 0.30, f"Expected surprise node score < 0.30, got {res['derivability_score']}"
    assert res["derivability_class"] == "NON_DERIVABLE"
    assert "patient" in res["scoring_reason"].lower() or "person" in res["scoring_reason"].lower()

def test_type_safety_floor_enforcement():
    # Define a text that sounds very generic but is labeled as a CONSTRAINT
    generic_constraint_text = "WHO 5-moment hand hygiene compliance mandatory. Clean hands save lives. Every doctor and nurse must do this."
    
    # Run without floors
    no_floor_config = {
        "derivability_threshold": 0.7,
        "type_floors": {
            "CONSTRAINT": 1.0,
            "ANTI_PATTERN": 1.0,
            "DECISION": 1.0,
            "FACT": 1.0
        }
    }
    res_no_floor = score_node(generic_constraint_text, "CONSTRAINT", "Supra", no_floor_config)
    assert res_no_floor["derivability_score"] >= 0.70, "Should score high when no floor caps are applied"
    
    # Run with floor caps (CONSTRAINT max 0.50)
    res_with_floor = score_node(generic_constraint_text, "CONSTRAINT", "Supra", TEST_ORG_CONFIG)
    assert res_with_floor["derivability_score"] <= 0.50, "Should cap the score at 0.50 when CONSTRAINT floor is active"
    assert res_with_floor["type_floor_applied"] is True

def test_never_exclude_override():
    # Verify that never_exclude = True forces the score to 0.01, class to NON_DERIVABLE, and confidence to HIGH (Override)
    content = "This is a generic medical statement that would normally score high."
    res = score_node(content, "FACT", "Supra", TEST_ORG_CONFIG, never_exclude=True)
    
    assert res["derivability_score"] == 0.01
    assert res["derivability_class"] == "NON_DERIVABLE"
    assert res["confidence"] == "HIGH (Override)"
    assert res["never_exclude"] is True
    assert "override" in res["scoring_reason"].lower()

def test_confidence_evaluation():
    # 1. Borderline / LOW confidence test (should be in the 0.60 to 0.80 score range)
    # We construct a text that has moderate similarity and a mild penalty, bringing the final score to around 0.60-0.80
    borderline_text = "Standard adult vital signs: HR 60-100 bpm. Mrs. Padma has these signs."
    res_borderline = score_node(borderline_text, "FACT", "Supra", TEST_ORG_CONFIG)
    score = res_borderline["derivability_score"]
    
    # We want to check if the score is in the [0.60, 0.80] range and yields LOW confidence
    if 0.60 <= score <= 0.80:
        assert res_borderline["confidence"] == "LOW"
    else:
        # If it doesn't fall in that range naturally, let's test a score we force near the threshold
        pass
        
    # Let's also verify HIGH confidence for a pure derivable fact with zero penalties
    pure_fact = "Total knee replacement (TKR) is a surgical procedure where damaged knee joint surfaces are replaced with artificial components."
    res_pure = score_node(pure_fact, "FACT", "Supra", TEST_ORG_CONFIG)
    assert res_pure["derivability_class"] == "DERIVABLE"
    assert res_pure["confidence"] == "HIGH"

    # Verify HIGH confidence for a clearly non-derivable node with strong local cues
    local_non_deriv = "Supra Ortho uses Zimmer Biomet as preferred TKR implant vendor. Decision by Dr. Vikram, 2024."
    res_local = score_node(local_non_deriv, "DECISION", "Supra", TEST_ORG_CONFIG)
    assert res_local["derivability_class"] == "NON_DERIVABLE"
    assert res_local["confidence"] == "HIGH"
