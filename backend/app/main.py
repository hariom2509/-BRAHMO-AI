from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from app.database import db
from app.scorer import score_node
from app.seed import seed_db

app = FastAPI(title="BRAHMO Derivability Scoring API", version="1.0.0")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- PYDANTIC SCHEMAS ---
class ConfigUpdateSchema(BaseModel):
    derivability_threshold: float = Field(..., ge=0.0, le=1.0)
    type_floors: Dict[str, float]

class SurpriseNodeSchema(BaseModel):
    content: str
    type: str = Field(..., description="Must be one of CONSTRAINT, DECISION, ANTI_PATTERN, FACT")
    never_exclude: Optional[bool] = False

@app.on_event("startup")
def startup_event():
    """Ensure organization exists on startup. If not, trigger seed."""
    org = db.get_organization("supra")
    if not org:
        print("Organization 'supra' not found on startup. Seeding database...")
        try:
            seed_db()
        except Exception as e:
            print(f"Error seeding database: {e}")

@app.get("/api/health")
def health_check():
    return {"status": "ok", "mode": "supabase" if db.is_supabase else "sqlite"}

@app.get("/api/org/{org_id}")
def get_org(org_id: str):
    org = db.get_organization(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

@app.post("/api/org/{org_id}/config")
def update_org_config(org_id: str, data: ConfigUpdateSchema):
    org = db.get_organization(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
        
    config = {
        "derivability_threshold": data.derivability_threshold,
        "type_floors": data.type_floors
    }
    
    success = db.update_organization_config(org_id, config)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update configuration")
        
    return {"status": "success", "config": config}

@app.get("/api/nodes")
def get_nodes(org_id: str = "supra"):
    return db.get_nodes(org_id)

@app.post("/api/rescore")
def rescore_nodes(org_id: str = "supra"):
    org = db.get_organization(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
        
    nodes = db.get_nodes(org_id)
    updated_nodes = []
    
    for node in nodes:
        scored = score_node(
            content=node["content"],
            node_type=node["type"],
            org_name="Supra",
            org_config=org["config"],
            never_exclude=bool(node.get("never_exclude", False))
        )
        
        # Prepare the updates
        updates = {
            "derivability_score": scored["derivability_score"],
            "derivability_class": scored["derivability_class"],
            "scoring_reason": scored["scoring_reason"],
            "type_floor_applied": scored["type_floor_applied"],
            "never_exclude": scored["never_exclude"],
            "confidence": scored["confidence"],
        }
        
        # Update delta content based on whether it is partial
        if scored["derivability_class"] == "PARTIALLY_DERIVABLE":
            # Keep manual override for seed nodes if present in original data
            # otherwise use automatically extracted portion
            if "non_derivable_portion" in node and node["non_derivable_portion"] and node["id"].startswith("E-"):
                updates["non_derivable_portion"] = node["non_derivable_portion"]
                updates["tokens_delta"] = node["tokens_delta"]
            else:
                updates["non_derivable_portion"] = scored["non_derivable_portion"]
                updates["tokens_delta"] = scored["tokens_delta"]
        else:
            updates["non_derivable_portion"] = scored["non_derivable_portion"]
            updates["tokens_delta"] = scored["tokens_delta"]
            
        db.update_node_scores(node["id"], updates)
        
        # Merge for response
        node.update(updates)
        updated_nodes.append(node)
        
    return updated_nodes

@app.post("/api/test-node")
def test_surprise_node(data: SurpriseNodeSchema, org_id: str = "supra"):
    org = db.get_organization(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
        
    # Check node type validity
    valid_types = ["CONSTRAINT", "DECISION", "ANTI_PATTERN", "FACT"]
    if data.type.upper() not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid type. Must be one of {valid_types}")
        
    scored = score_node(
        content=data.content,
        node_type=data.type.upper(),
        org_name="Supra",
        org_config=org["config"],
        never_exclude=bool(data.never_exclude)
    )
    
    return {
        "content": data.content,
        "type": data.type.upper(),
        "derivability_score": scored["derivability_score"],
        "derivability_class": scored["derivability_class"],
        "scoring_reason": scored["scoring_reason"],
        "type_floor_applied": scored["type_floor_applied"],
        "non_derivable_portion": scored["non_derivable_portion"],
        "tokens_delta": scored["tokens_delta"],
        "confidence": scored["confidence"],
        "never_exclude": scored["never_exclude"]
    }

@app.post("/api/seed")
def trigger_seed():
    try:
        seed_db()
        return {"status": "success", "message": "Database seeded successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
