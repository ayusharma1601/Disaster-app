import sys
import os
from datetime import datetime, timedelta

# Add parent path to import services
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.data_validation import validate_coordinates, validate_and_parse_csv
from services.risk_engine import RiskEngine

def test_geographic_boundary():
    # Valid Guwahati coords
    assert validate_coordinates(26.1422, 91.7898) is True
    # Andhra Pradesh coords (must fail)
    assert validate_coordinates(14.6819, 77.6006) is False

def test_reject_wrong_state():
    # Test rejection of the old demo_data.csv (Andhra Pradesh)
    old_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "demo_data.csv"))
    res = validate_and_parse_csv(old_csv)
    assert res["rejected_count"] > 0
    assert "Geographic mismatch" in res["rejected_rows"][0]["reason"]

def test_parse_valid_assam_data():
    assam_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "sample", "assam_kamrup_demo.csv"))
    res = validate_and_parse_csv(assam_csv)
    assert res["valid_count"] > 0
    # Check null preservation
    khanapara = next(r for r in res["valid_rows"] if "Khanapara" in r["station_name"])
    assert khanapara["value"] is None
    assert khanapara["quality_flag"] == "MISSING"

def test_risk_stale_data():
    stale_time = datetime.utcnow() - timedelta(hours=14)
    obs = [{
        "station_name": "Dispur",
        "variable": "rainfall_24h",
        "value": 150.0,
        "observed_at": stale_time
    }]
    result = RiskEngine.evaluate_risk(obs)
    assert "STALE DATA" in result["category"]

def test_risk_high_rainfall():
    fresh_time = datetime.utcnow() - timedelta(hours=2)
    obs = [{
        "station_name": "Chandmari",
        "variable": "rainfall_24h",
        "value": 140.0,  # Very heavy
        "observed_at": fresh_time
    }]
    result = RiskEngine.evaluate_risk(obs)
    assert result["category"] == "MODERATE" or result["category"] == "HIGH"

if __name__ == "__main__":
    test_geographic_boundary()
    test_reject_wrong_state()
    test_parse_valid_assam_data()
    test_risk_stale_data()
    test_risk_high_rainfall()
    print("All unit tests passed successfully!")
