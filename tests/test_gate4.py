"""
Gate 4 Verification & Test Suite: Community Reporting & Responder Workflow
Uses standard library urllib.request to avoid external dependency.
Tests the 3 requirements of Gate 4 in ROADMAP_AND_EVALUATION_PLAN.md:
1. Public incident submissions always enter the database as UNVERIFIED.
2. Public views (/api/incidents) sanitize reporter phone numbers and contact details.
3. Protected responder endpoints (/api/incidents/{id}/status) reject unauthenticated requests with HTTP 401.
4. State machine allows only valid transitions and rejects invalid jumps with HTTP 400.
"""

import os
import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8000"

def make_req(url, method="GET", payload=None, headers=None):
    if headers is None:
        headers = {}
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            status = response.getcode()
            body = response.read().decode("utf-8")
            return status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return e.code, parsed

def test_gate4():
    print("=" * 65)
    print("RUNNING GATE 4 EVALUATION & VERIFICATION SUITE")
    print("=" * 65)

    # 1. Test Unauthenticated Public Incident Submission
    print("\n[CHECK 1] Incident Submission always enters as UNVERIFIED:")
    new_report = {
        "category": "Waterlogging",
        "location_text": "Dhemaji ASTC Bus Stand",
        "description": "Rising water on platforms, 0.4m depth observed.",
        "urgency": "HIGH",
        "latitude": 27.4811,
        "longitude": 94.5822,
        "reporter_contact": "+91-9876543210 (CONFIDENTIAL)"
    }
    status, inc_data = make_req(f"{BASE_URL}/api/incidents", method="POST", payload=new_report)
    assert status == 200, f"Submission failed: {inc_data}"
    assert inc_data["status"] == "UNVERIFIED", f"Expected UNVERIFIED, got {inc_data['status']}"
    created_id = inc_data["id"]
    print(f"  --> PASSED: Incident #{created_id} created with initial status: {inc_data['status']}")

    # 2. Test Privacy Leak Prevention (Reporter Contact Not Leaked)
    print("\n[CHECK 2] Public Incident Feed sanitizes reporter contact numbers:")
    feed_status, feed_items = make_req(f"{BASE_URL}/api/incidents", method="GET")
    assert feed_status == 200, f"Failed to get feed: {feed_items}"
    
    our_incident = next((i for i in feed_items if i["id"] == created_id), None)
    assert our_incident is not None, "Created incident not found in public list"
    assert "reporter_contact" not in our_incident, "SECURITY LEAK: 'reporter_contact' exposed in public API response!"
    print(f"  --> PASSED: 'reporter_contact' field is absent from IncidentResponse schema. Zero PII leakage.")

    # 3. Test RBAC Security on Responder Status Endpoint (No Auth -> 401)
    print("\n[CHECK 3] Unauthorized requests to status mutation endpoint are rejected:")
    unauth_status, unauth_body = make_req(
        f"{BASE_URL}/api/incidents/{created_id}/status",
        method="PATCH",
        payload={"new_status": "VERIFIED", "note": "Malicious tampering"}
    )
    assert unauth_status == 401, f"Expected 401 Unauthorized, got {unauth_status}"
    print(f"  --> PASSED: HTTP 401 properly returned for unauthenticated status transition.")

    # 4. Test Valid & Invalid State Machine Transitions
    print("\n[CHECK 4] Operator login and State Machine deterministic progression:")
    login_status, login_res = make_req(f"{BASE_URL}/api/auth/login", method="POST", payload={
        "username": "operator",
        "password": "operator123"
    })
    assert login_status == 200, f"Login failed: {login_res}"
    token = login_res["token"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    print(f"  --> Operator logged in successfully as {login_res['username']} ({login_res['role']}).")

    # Invalid jump: UNVERIFIED -> RESOLVED should fail (HTTP 400)
    invalid_status, invalid_body = make_req(
        f"{BASE_URL}/api/incidents/{created_id}/status",
        method="PATCH",
        payload={"new_status": "RESOLVED", "note": "Illegal shortcut"},
        headers=auth_headers
    )
    assert invalid_status == 400, f"Expected 400 for illegal transition, got {invalid_status}"
    print(f"  --> PASSED: Illegal transition UNVERIFIED -> RESOLVED correctly rejected with HTTP 400.")

    # Valid transition: UNVERIFIED -> VERIFIED
    s1_status, s1_body = make_req(
        f"{BASE_URL}/api/incidents/{created_id}/status",
        method="PATCH",
        payload={"new_status": "VERIFIED", "note": "Verified by SDRF Field Unit 4"},
        headers=auth_headers
    )
    assert s1_status == 200, f"Transition failed: {s1_body}"
    assert s1_body["new_status"] == "VERIFIED"
    print(f"  --> Transition 1 PASSED: UNVERIFIED -> VERIFIED")

    # Valid transition: VERIFIED -> ASSIGNED
    s2_status, s2_body = make_req(
        f"{BASE_URL}/api/incidents/{created_id}/status",
        method="PATCH",
        payload={"new_status": "ASSIGNED", "note": "Assigned to Dhemaji Municipal SDRF"},
        headers=auth_headers
    )
    assert s2_status == 200, f"Transition failed: {s2_body}"
    assert s2_body["new_status"] == "ASSIGNED"
    print(f"  --> Transition 2 PASSED: VERIFIED -> ASSIGNED")

    # Valid transition: ASSIGNED -> IN PROGRESS
    s3_status, s3_body = make_req(
        f"{BASE_URL}/api/incidents/{created_id}/status",
        method="PATCH",
        payload={"new_status": "IN PROGRESS", "note": "Pumping water with dewatering pumps"},
        headers=auth_headers
    )
    assert s3_status == 200, f"Transition failed: {s3_body}"
    assert s3_body["new_status"] == "IN PROGRESS"
    print(f"  --> Transition 3 PASSED: ASSIGNED -> IN PROGRESS")

    # Valid transition: IN PROGRESS -> RESOLVED
    s4_status, s4_body = make_req(
        f"{BASE_URL}/api/incidents/{created_id}/status",
        method="PATCH",
        payload={"new_status": "RESOLVED", "note": "Water drained completely, road cleared"},
        headers=auth_headers
    )
    assert s4_status == 200, f"Transition failed: {s4_body}"
    assert s4_body["new_status"] == "RESOLVED"
    print(f"  --> Transition 4 PASSED: IN PROGRESS -> RESOLVED")

    # Valid transition: RESOLVED -> CLOSED
    s5_status, s5_body = make_req(
        f"{BASE_URL}/api/incidents/{created_id}/status",
        method="PATCH",
        payload={"new_status": "CLOSED", "note": "Case closed post-inspection"},
        headers=auth_headers
    )
    assert s5_status == 200, f"Transition failed: {s5_body}"
    assert s5_body["new_status"] == "CLOSED"
    print(f"  --> Transition 5 PASSED: RESOLVED -> CLOSED")

    print("\n" + "=" * 65)
    print("ALL GATE 4 CRITERIA FULLY SATISFIED AND VALIDATED!")
    print("=" * 65)

if __name__ == "__main__":
    test_gate4()
