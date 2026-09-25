from __future__ import annotations

import json
import os
import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# Ensure project root is in python path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR))

from src.prediction.predictor import Predictor, _compose_specs
from src.prediction.spec_coach import coach_spec
from src.prediction.input_gate import evaluate_sufficiency

app = FastAPI(title="Hybrid AI Product Success Predictor API", version="1.0.0")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PHYSICAL_CATEGORIES = ["wireless_headphones", "bluetooth_speakers", "ice_makers",
                       "smartwatches", "power_banks"]
APP_CATEGORIES: list[str] = []  # apps removed from the system

PROFILES_PATH = ROOT_DIR / "data/extracted/category_profiles.json"
SPEC_SCHEMA_PATH = ROOT_DIR / "config/category_specs.json"

class PredictRequest(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., ge=0.0)
    # description is optional at the API boundary: sufficiency is enforced by the
    # input gate (which also accepts structured specs), not by Pydantic min_length.
    description: str = ""
    category: str = Field(..., min_length=1)
    specs: dict = Field(default_factory=dict)          # structured category-specific fields
    company_maturity: str | None = None                # 'new' | 'established'
    product_maturity: str | None = None                # 'new' | 'iterated'
    mock: bool = False

class CoachRequest(BaseModel):
    price: float = Field(..., ge=0.0)
    description: str = ""
    category: str = Field(..., min_length=1)
    specs: dict = Field(default_factory=dict)
    mock: bool = False

@app.get("/api/categories")
def get_categories():
    return {
        "physical": PHYSICAL_CATEGORIES,
        "app": APP_CATEGORIES
    }

@app.get("/api/spec_schema")
def get_spec_schema():
    """Serve the schema-driven category specification fields (Requirement 1).
    Adding a category/field is a JSON edit — no code change, no rebuild."""
    if not SPEC_SCHEMA_PATH.exists():
        return {"categories": {}}
    with open(SPEC_SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)

@app.get("/api/profile/{category}")
def get_profile(category: str):
    if not PROFILES_PATH.exists():
        raise HTTPException(status_code=500, detail="Category profiles not found. Run training pipeline first.")
    
    with open(PROFILES_PATH, encoding="utf-8") as f:
        profiles = json.load(f)
        
    if category not in profiles:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found.")
        
    return profiles[category]

@app.get("/api/analyzer")
def get_analyzer_report():
    report_path = ROOT_DIR / "models/training_report.json"
    if not report_path.exists():
        raise HTTPException(status_code=500, detail="Training report not found. Run training pipeline first.")
    with open(report_path, encoding="utf-8") as f:
        return json.load(f)

@app.post("/api/predict")
def predict_success(req: PredictRequest):
    try:
        # Requirement 3: refuse to predict on insufficient input, BEFORE any LLM call.
        gate = evaluate_sufficiency(req.description, req.price, req.specs)
        if not gate["sufficient"]:
            return {"refused": True, **gate}

        predictor = Predictor(use_mock_llm=req.mock)
        specs = {
            "name": req.name,
            "price": req.price,
            "description": req.description.strip(),
            "specs": req.specs,
            "company_maturity": req.company_maturity,
            "product_maturity": req.product_maturity,
        }
        result = predictor.predict(specs, req.category)
        result["refused"] = False
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/coach")
def coach_specification(req: CoachRequest):
    try:
        if not PROFILES_PATH.exists():
            raise HTTPException(status_code=500, detail="Category profiles not found. Run training pipeline first.")
        
        with open(PROFILES_PATH, encoding="utf-8") as f:
            profiles = json.load(f)
            
        if req.category not in profiles:
            raise HTTPException(status_code=404, detail=f"Category '{req.category}' not found.")
            
        ptype = "physical" if req.category in PHYSICAL_CATEGORIES else "app"
        # Fold structured specs into the description so the coach reviews them too.
        user_specs = _compose_specs({
            "price": req.price,
            "description": req.description.strip(),
            "specs": req.specs,
        })

        coach_result = coach_spec(
            user_specs=user_specs,
            category=req.category,
            profile=profiles[req.category],
            product_type=ptype,
            use_mock=req.mock
        )
        return coach_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount compiled static React files if build directory exists
FRONTEND_DIR = Path(__file__).resolve().parent / "frontend/dist"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
    
    @app.exception_handler(404)
    async def custom_404_handler(request, __):
        # Fallback to index.html for SPA client-side routing
        return FileResponse(FRONTEND_DIR / "index.html")

if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
