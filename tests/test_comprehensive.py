import os
import sys
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from database import Base
import models
from services.data_validation import validate_coordinates, validate_and_parse_csv
from services.risk_engine import RiskEngine

TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def run_all_comprehensive_tests():
    print("=================================================================")
    print("STARTING COMPREHENSIVE PLATFORM TEST SUITE & BOUNDARY EVALUATION")
    print("=================================================================\n")

    # -------------------------------------------------------------
    # Test 1: Coordinate Boundary Edge Cases
    # -------------------------------------------------------------
    print("[TEST 1] Geographic Boundary Extreme Tests:")
    assert validate_coordinates(24.0, 92.0) is True, "Min latitude bound failed"
    assert validate_coordinates(28.2, 92.0) is True, "Max latitude bound failed"
    assert validate_coordinates(26.0, 89.7) is True, "Min longitude bound failed"
    assert validate_coordinates(26.0, 96.1) is True, "Max longitude bound failed"
    # Off-by-one boundary violations
    assert validate_coordinates(23.9999, 92.0) is False, "South boundary leak"
    assert validate_coordinates(28.2001, 92.0) is False, "North boundary leak"
    assert validate_coordinates(26.0, 89.6999) is False, "West boundary leak"
    assert validate_coordinates(26.0, 96.1001) is False, "East boundary leak"
    # International / Out of state coordinates
    assert validate_coordinates(0.0, 0.0) is False, "Null island leak"
    assert validate_coordinates(14.68, 77.60) is False, "Andhra Pradesh leak"
    print("  --> Passed: All edge coordinates strictly guarded.\n")

    # -------------------------------------------------------------
    # Test 2: Ingestion Robustness & Quality Flags
    # -------------------------------------------------------------
    print("[TEST 2] CSV Ingestion & Quality Flags:")
    dhemaji_csv = os.path.join(BASE_DIR, "data", "sample", "dhemaji_telemetry.csv")
    parsed = validate_and_parse_csv(dhemaji_csv)
    assert parsed["valid_count"] > 0, "Dhemaji valid rows failed to parse"
    assert parsed["rejected_count"] == 0, f"Dhemaji had unexpected rejections: {parsed['rejected_rows']}"
    
    # Check null sensor value handling (FR-015)
    sissiborgaon = next(r for r in parsed["valid_rows"] if "Sissiborgaon" in r["station_name"])
    assert sissiborgaon["value"] is None, "Missing sensor value was not preserved as None"
    assert sissiborgaon["quality_flag"] == "MISSING", "Quality flag for missing sensor was not set"
    print("  --> Passed: Null values preserved; quality flags properly labeled.\n")

    # -------------------------------------------------------------
    # Test 3: Risk Engine Boundary & Stress Tests
    # -------------------------------------------------------------
    print("[TEST 3] Risk Engine Behavior Across Critical Thresholds:")
    now = datetime.now(timezone.utc)

    # Empty inputs -> DATA UNAVAILABLE
    res_empty = RiskEngine.evaluate_risk([])
    assert res_empty["category"] == "DATA UNAVAILABLE", "Empty telemetry should yield DATA UNAVAILABLE"

    # Stale data (> 12 hours) -> STALE DATA
    stale_time = now - timedelta(hours=12, minutes=5)
    res_stale = RiskEngine.evaluate_risk([{
        "station_name": "Jonai",
        "variable": "rainfall_24h",
        "value": 250.0,
        "observed_at": stale_time
    }])
    assert "STALE DATA" in res_stale["category"], "Stale data failed to trigger safety fallback"

    # Exact threshold boundary: 64.4mm vs 65.0mm
    fresh_time = now - timedelta(hours=1)
    res_boundary_low = RiskEngine.evaluate_risk([{
        "station_name": "Silapathar",
        "variable": "rainfall_24h",
        "value": 64.4,
        "observed_at": fresh_time
    }])
    assert res_boundary_low["category"] == "LOW", "64.4mm should be LOW"

    # River Gauge Danger Level Breach -> HIGH
    res_river_danger = RiskEngine.evaluate_risk([{
        "station_name": "Subansiri River Confluence",
        "variable": "water_level",
        "value": 86.5,  # danger level is 86.0
        "warning_level": 85.0,
        "danger_level": 86.0,
        "observed_at": fresh_time
    }])
    assert res_river_danger["category"] == "HIGH", f"River danger breach should trigger HIGH, got {res_river_danger['category']}"
    assert any("at/above Danger Level" in reason for reason in res_river_danger["reasons"])
    print("  --> Passed: Risk thresholds and danger levels trigger exact deterministic outcomes.\n")

    # -------------------------------------------------------------
    # Test 4: Database Model Integrity & Incident Transitions
    # -------------------------------------------------------------
    print("[TEST 4] Database Integrity & Incident State Machine:")
    db = TestingSessionLocal()
    try:
        # Create Incident (Starts UNVERIFIED)
        inc = models.Incident(
            category="River Embankment Breach",
            description="Seepage along Sissiborgaon bund section 4.",
            location_text="Sissiborgaon Ward 3",
            latitude=27.51,
            longitude=94.67,
            urgency="CRITICAL",
            status="UNVERIFIED"
        )
        db.add(inc)
        db.commit()
        db.refresh(inc)
        assert inc.id is not None
        assert inc.status == "UNVERIFIED"

        # Record Initial Event
        evt1 = models.IncidentEvent(
            incident_id=inc.id,
            actor_name="Public Reporter",
            old_status=None,
            new_status="UNVERIFIED",
            note="Initial report submission via web interface."
        )
        db.add(evt1)
        db.commit()

        # Responder Verifies Report
        inc.status = "VERIFIED"
        evt2 = models.IncidentEvent(
            incident_id=inc.id,
            actor_name="Dhemaji District Control Room",
            old_status="UNVERIFIED",
            new_status="VERIFIED",
            note="Confirmed on-ground by Circle Officer."
        )
        db.add(evt2)
        db.commit()

        # Responder Resolves Report
        inc.status = "RESOLVED"
        evt3 = models.IncidentEvent(
            incident_id=inc.id,
            actor_name="SDRF Response Leader",
            old_status="VERIFIED",
            new_status="RESOLVED",
            note="Sandbag reinforcement completed."
        )
        db.add(evt3)
        db.commit()

        # Verify Audit History
        events = db.query(models.IncidentEvent).filter(models.IncidentEvent.incident_id == inc.id).order_by(models.IncidentEvent.created_at.asc()).all()
        assert len(events) == 3
        assert events[0].new_status == "UNVERIFIED"
        assert events[1].new_status == "VERIFIED"
        assert events[2].new_status == "RESOLVED"
        print("  --> Passed: Database audit transitions and relationships verified completely.\n")
    finally:
        db.close()

    print("=================================================================")
    print("ALL TESTS COMPLETED SUCCESSFULLY! ZERO ERRORS OR LEAKS DETECTED.")
    print("=================================================================")

if __name__ == "__main__":
    run_all_comprehensive_tests()
