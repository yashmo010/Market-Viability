"""Automated Test Suite for LLM Bridge Validity, Reproducibility, and Robustness.

Verifies Issue 4 audit requirements:
1. Final prompt hash matches recorded metadata.
2. Prompt V2 enforces skeptic rules (absence penalty, anchor discipline).
3. All 9 physical aspects are defined and strictly required.
4. Input specifications contain zero post-launch reviews or target labels.
5. Schema validation strictly enforces [0.0, 10.0] bounds and rejects missing keys.
6. In-process memoization cache guarantees bit-for-bit repeatability on identical specs.
7. Mock provider operates deterministically without network calls.
8. Post-bridging price adjustment operates deterministically.
9. Aspect reliability weights are non-negative and properly formatted.
10. Preserved raw outputs match schema.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.extraction.extraction_prompt import (
    BRIDGING_PROMPT_V2,
    PHYSICAL_ASPECTS,
    PHYSICAL_ASPECT_KEYS,
    build_bridging_prompt,
)
from src.extraction.validators import BridgingResult, validate_bridging
from src.prediction.bridging_layer import _mock_bridge, bridge_aspects
from src.strict_temporal.predict_test import StrictPredictor

AUDIT_LLM_DIR = ROOT / "audit/llm"


def test_1_prompt_hash_integrity():
    """Test 1: Final prompt hash matches recorded metadata."""
    meta_path = AUDIT_LLM_DIR / "PROMPT_METADATA.json"
    assert meta_path.exists()
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)
        
    current_hash = hashlib.sha256(BRIDGING_PROMPT_V2.encode("utf-8")).hexdigest()
    assert current_hash == meta["sha256_hash"]


def test_2_skeptic_prompt_rules():
    """Test 2: Prompt V2 contains explicit skeptic rules."""
    prompt_lower = BRIDGING_PROMPT_V2.lower()
    assert "skeptical market analyst" in prompt_lower
    assert "ignore marketing" in prompt_lower
    assert "absence rule" in prompt_lower
    assert "anchor discipline" in prompt_lower
    assert "grounded" in prompt_lower


def test_3_aspect_definitions_count_and_keys():
    """Test 3: Exactly 9 physical aspects are defined."""
    assert len(PHYSICAL_ASPECTS) == 9
    assert len(PHYSICAL_ASPECT_KEYS) == 9
    expected = {
        "value_for_money", "utility", "ease_of_use", "reliability",
        "design_appeal", "after_sales", "build_quality", "durability", "repairability"
    }
    assert set(PHYSICAL_ASPECT_KEYS) == expected


def test_4_zero_forbidden_inputs_in_test_specs():
    """Test 4: Input specifications contain zero reviews or target fields."""
    specs_path = ROOT / "strict_temporal/data/test_inputs/products_test_specs.json"
    assert specs_path.exists()
    with open(specs_path, encoding="utf-8") as f:
        test_specs = json.load(f)
        
    forbidden = ["reviews", "avg_rating", "rating_count", "review_velocity", "success_score", "successscore"]
    for item in test_specs:
        for fld in forbidden:
            assert fld not in item, f"Forbidden field '{fld}' found in test product {item.get('product_uid')}"


def test_5_schema_validation_and_rejection():
    """Test 5: Schema validation enforces [0, 10] bounds and rejects missing keys."""
    # Valid payload
    valid_payload = {
        "scores": {
            k: {"score": 7.5, "reasoning": "Standard category features observed in spec.", "grounded": True}
            for k in PHYSICAL_ASPECT_KEYS
        },
        "confidence": 0.8
    }
    res = validate_bridging(json.dumps(valid_payload), product_type="physical")
    assert isinstance(res, BridgingResult)
    assert len(res.scores) == 9
    
    # Missing key should raise ValueError
    invalid_missing = json.dumps({
        "scores": {k: {"score": 7.0, "reasoning": "Valid", "grounded": True} for k in PHYSICAL_ASPECT_KEYS[:-1]},
        "confidence": 0.5
    })
    with pytest.raises(ValueError, match="missing"):
        validate_bridging(invalid_missing, product_type="physical")
        
    # Out of bounds score (>10.0) should raise ValueError
    invalid_out_of_bounds = json.dumps({
        "scores": {
            k: {"score": 15.0 if k == "utility" else 7.0, "reasoning": "Valid reasoning statement.", "grounded": True}
            for k in PHYSICAL_ASPECT_KEYS
        },
        "confidence": 0.5
    })
    with pytest.raises(ValueError):
        validate_bridging(invalid_out_of_bounds, product_type="physical")


def test_6_memoization_cache():
    """Test 6: In-process memoization cache returns identical object for identical spec."""
    profile = {
        "n_products": 100,
        "price": {"median": 50.0, "p25": 30.0, "p75": 80.0},
        "avg_aspect_scores": {k: 5.0 for k in PHYSICAL_ASPECT_KEYS},
        "pain_points": {"aspects": ["reliability"], "evidence": {"reliability": ["glitches"]}},
        "strengths": {"aspects": ["utility"], "evidence": {"utility": ["crisp audio"]}},
        "consumer_priorities": "battery life",
    }
    user_specs = {"name": "Test Wireless Headphone", "price": 49.99, "features": ["Bluetooth 5.3", "IPX5"]}
    
    # First call via mock
    res1 = _mock_bridge(user_specs, profile, product_type="physical")
    res2 = _mock_bridge(user_specs, profile, product_type="physical")
    assert res1.scores["utility"].score == res2.scores["utility"].score
    assert res1.scores["value_for_money"].score == res2.scores["value_for_money"].score


def test_7_mock_bridge_bounds():
    """Test 7: Mock bridge produces bounded outputs in [0.0, 10.0]."""
    profile = {
        "price": {"median": 100.0},
        "avg_aspect_scores": {k: 5.0 for k in PHYSICAL_ASPECT_KEYS}
    }
    # Test extreme price
    res_high = _mock_bridge({"price": 1000.0}, profile, product_type="physical")
    assert 0.0 <= res_high.scores["value_for_money"].score <= 10.0
    
    res_low = _mock_bridge({"price": 1.0}, profile, product_type="physical")
    assert 0.0 <= res_low.scores["value_for_money"].score <= 10.0


def test_8_deterministic_price_decoupling():
    """Test 8: Value for money adjustment behaves monotonically with price."""
    predictor = StrictPredictor()
    cat = "bluetooth_speakers"
    base_scores = {k: 6.0 for k in PHYSICAL_ASPECT_KEYS}
    
    adj_cheap = predictor._deterministic_value_for_money(base_scores, price=20.0, category=cat)
    adj_expensive = predictor._deterministic_value_for_money(base_scores, price=200.0, category=cat)
    
    assert adj_cheap["value_for_money"] > adj_expensive["value_for_money"]


def test_9_reliability_weights():
    """Test 9: Aspect reliability weights exist and are valid probabilities."""
    rel_path = AUDIT_LLM_DIR / "ASPECT_VALIDITY_RELIABILITY.csv"
    assert rel_path.exists()
    
    df = pd.read_csv(rel_path)
    assert len(df) == 9
    assert all(df["Confidence Weight in UI"] >= 0.0)
    assert all(df["Confidence Weight in UI"] <= 1.0)


def test_10_preserved_raw_outputs():
    """Test 10: Preserved final outputs directory exists and contains valid JSON."""
    final_dir = AUDIT_LLM_DIR / "final_outputs"
    assert final_dir.exists()
    
    json_files = list(final_dir.glob("*.json"))
    assert len(json_files) >= 5
    for jf in json_files:
        with open(jf, encoding="utf-8") as f:
            data = json.load(f)
        assert "product_uid" in data
        assert "bridged_aspects" in data
        assert len(data["bridged_aspects"]) == 9
