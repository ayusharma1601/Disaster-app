"""
Master Platform Test Runner
Executes all Gate verification test suites:
- tests/test_core.py (Data ingestion & coordinate bounds)
- tests/test_comprehensive.py (Risk engine thresholds & state machines)
- tests/test_gate4.py (Incident workflow & privacy protection)
- tests/test_gate5.py (Resource allocation & 24h shelter freshness)
- tests/test_gate7.py (Web security headers, XSS, rate limiting)
- simulate_demo_cycle.py (End-to-end full operational cycle)
"""

import subprocess
import sys
import os

SCRIPTS = [
    ("tests/test_core.py", "Core Bounds & Ingestion"),
    ("tests/test_comprehensive.py", "Comprehensive Boundaries & Quality Flags"),
    ("tests/test_gate4.py", "Gate 4: Incident State Machine & Privacy"),
    ("tests/test_gate5.py", "Gate 5: Resource Registry & Shelter Freshness"),
    ("tests/test_gate7.py", "Gate 7: Security Headers, XSS & Rate Limiting"),
    ("simulate_demo_cycle.py", "Phase 6: End-to-End Operational Simulation")
]

def run_all():
    print("=" * 70)
    print("RUNNING ALL PLATFORM TEST SUITES & QUALITY GATES")
    print("=" * 70)
    passed = 0
    total = len(SCRIPTS)

    for script, desc in SCRIPTS:
        print(f"\n>> Running: {desc} ({script})...")
        res = subprocess.run([sys.executable, script], capture_output=True, text=True)
        if res.returncode == 0:
            print(f"   [PASS] {desc}")
            passed += 1
        else:
            print(f"   [FAIL] {desc}")
            print(res.stdout)
            print(res.stderr)

    pass_rate = round((passed / max(1, total)) * 100, 1)
    print("\n" + "=" * 70)
    print(f"ALL TESTS COMPLETED: {passed}/{total} SUITES PASSED ({pass_rate}% PASS RATE)")
    print("=" * 70)
    if passed < total:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    run_all()
