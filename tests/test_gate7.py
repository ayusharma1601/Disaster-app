"""
Gate 7 Verification & Test Suite: Terms & Conditions & Web Application Security Hardening
Tests all requirements of Gate 7 in ROADMAP_AND_EVALUATION_PLAN.md:
1. Security Headers: Verified presence of X-Frame-Options (DENY), X-Content-Type-Options (nosniff),
   Content-Security-Policy, and Referrer-Policy on responses.
2. XSS Input Sanitization: Submitting malicious HTML/JavaScript payloads (<script>alert('xss')</script>)
   in incident description or location fields gets properly escaped to prevent stored XSS attacks.
3. Rate Limiting / DoS Protection: High-velocity bursts to /api/auth/login are throttled with HTTP 429.
4. Terms & Conditions: Accessible at /terms with life-safety disclaimers and emergency helplines (112 / 1070).
"""

import os
import sys
import json
import urllib.request
import urllib.error

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

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
            resp_headers = dict(response.info())
            body = response.read().decode("utf-8")
            try:
                parsed = json.loads(body)
            except Exception:
                parsed = body
            return status, parsed, resp_headers
    except urllib.error.HTTPError as e:
        resp_headers = dict(e.headers)
        body = e.read().decode("utf-8")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return e.code, parsed, resp_headers

def test_gate7():
    print("=" * 65)
    print("RUNNING GATE 7 EVALUATION & SECURITY HARDENING TEST SUITE")
    print("=" * 65)

    # 1. Test Security Headers
    print("\n[CHECK 1] HTTP Security Headers Middleware Verification:")
    status, _, headers = make_req(f"{BASE_URL}/")
    assert status == 200, "Dashboard failed to respond"

    # Normalize header keys to lowercase
    lower_headers = {k.lower(): v for k, v in headers.items()}
    
    # Check X-Frame-Options
    assert "x-frame-options" in lower_headers, "Missing X-Frame-Options header!"
    assert lower_headers["x-frame-options"] == "DENY", f"Expected 'DENY', got '{lower_headers['x-frame-options']}'"
    print("  --> PASSED: X-Frame-Options: DENY (Clickjacking protection active)")

    # Check X-Content-Type-Options
    assert "x-content-type-options" in lower_headers, "Missing X-Content-Type-Options header!"
    assert lower_headers["x-content-type-options"] == "nosniff", f"Expected 'nosniff', got '{lower_headers['x-content-type-options']}'"
    print("  --> PASSED: X-Content-Type-Options: nosniff (MIME sniffing blocked)")

    # Check Content-Security-Policy
    assert "content-security-policy" in lower_headers, "Missing Content-Security-Policy header!"
    csp = lower_headers["content-security-policy"]
    assert "default-src 'self'" in csp, "CSP default-src missing"
    assert "frame-ancestors 'none'" in csp, "CSP frame-ancestors missing"
    print("  --> PASSED: Content-Security-Policy active with strict default-src and frame-ancestors restrictions")

    # Check Referrer-Policy
    assert "referrer-policy" in lower_headers, "Missing Referrer-Policy header!"
    print(f"  --> PASSED: Referrer-Policy: {lower_headers['referrer-policy']}")

    # 2. Test Stored XSS Script Payload Sanitization
    print("\n[CHECK 2] Anti-XSS Sanitization on User Submissions:")
    xss_payload = "<script>alert('MALICIOUS_TOKEN_STEALER')</script>"
    xss_location = "<b onmouseover=alert('XSS')>Test Landmark</b>"

    submit_status, submit_res, _ = make_req(f"{BASE_URL}/api/incidents", method="POST", payload={
        "category": "Waterlogging",
        "location_text": xss_location,
        "description": xss_payload,
        "urgency": "HIGH",
        "latitude": 27.4833,
        "longitude": 94.5833
    })
    assert submit_status == 200, f"Submission failed: {submit_res}"
    created_id = submit_res["id"]

    # Verify that raw script tags were sanitized and escaped
    assert "<script>" not in submit_res["description"], "SECURITY FAILURE: Raw <script> tag preserved in response!"
    assert "&lt;script&gt;" in submit_res["description"], f"Expected escaped HTML, got: {submit_res['description']}"
    assert "<b onmouseover" not in submit_res["location_text"], "SECURITY FAILURE: Raw event handler tag preserved!"
    print(f"  --> PASSED: Stored XSS neutralized. Description escaped to: {submit_res['description']}")
    print(f"  --> PASSED: Landmark escaped to: {submit_res['location_text']}")

    # 3. Test Terms & Conditions Page
    print("\n[CHECK 3] Terms & Conditions & Statutory Disclaimer Page:")
    terms_status, terms_html, _ = make_req(f"{BASE_URL}/terms")
    assert terms_status == 200, "Terms page not accessible!"
    assert "NOT AN EMERGENCY DISPATCH SYSTEM" in terms_html, "Missing emergency dispatch warning"
    assert "112" in terms_html and "1070" in terms_html, "Missing national emergency helpline numbers"
    assert "Disaster Management Act" in terms_html, "Missing statutory legal reference"
    print("  --> PASSED: /terms route accessible with explicit life-safety disclaimers and emergency helplines (112 / 1070).")

    # 4. Test Login Rate Limiting (Anti-Brute Force)
    print("\n[CHECK 4] Anti-Brute Force Rate Limiting on /api/auth/login:")
    rate_limited = False
    # Attempt rapid sequence of bad logins (burst limit: 10 attempts per min)
    for i in range(12):
        st, res, _ = make_req(f"{BASE_URL}/api/auth/login", method="POST", payload={
            "username": "attacker",
            "password": f"badpass_{i}"
        })
        if st == 429:
            rate_limited = True
            print(f"  --> PASSED: Attempt #{i+1} throttled with HTTP 429 Rate Limit Exceeded: {res.get('detail')}")
            break

    assert rate_limited, "Rate limiter failed to block rapid brute-force burst!"

    print("\n" + "=" * 65)
    print("ALL GATE 7 CRITERIA FULLY SATISFIED AND HARDENED!")
    print("=" * 65)

if __name__ == "__main__":
    test_gate7()
