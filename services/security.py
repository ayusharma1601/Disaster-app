"""
Web Application Security Middleware & Utilities
Provides:
1. Input sanitization (anti-XSS HTML escaping).
2. Rate Limiting via in-memory sliding token bucket per client IP.
3. HTTP Security Headers enforcement (CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy).
"""

import html
import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

def sanitize_input(text: str) -> str:
    """Sanitize user-provided text by HTML-escaping script and tag characters."""
    if not text:
        return ""
    # Strip dangerous characters and escape HTML
    cleaned = html.escape(text.strip())
    # Replace dangerous javascript: pseudo-protocols
    cleaned = cleaned.replace("javascript:", "").replace("vbscript:", "")
    return cleaned

class RateLimiter:
    """In-memory rate limiter per IP address using token bucket/sliding counter."""
    def __init__(self, requests_per_minute: int = 60, burst_limit: int = 15):
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        # ip -> list of timestamps
        self.history: Dict[str, list] = {}

    def is_allowed(self, ip: str) -> Tuple[bool, int]:
        now = time.time()
        window_start = now - 60.0

        if ip not in self.history:
            self.history[ip] = []

        # Clean entries older than 60 seconds
        self.history[ip] = [ts for ts in self.history[ip] if ts > window_start]

        if len(self.history[ip]) >= self.requests_per_minute:
            retry_after = int(60.0 - (now - self.history[ip][0]))
            return False, max(1, retry_after)

        self.history[ip].append(now)
        return True, 0

    def reset_ip(self, ip: str):
        """Clear rate limit history for a specific IP (for test runners)."""
        if ip in self.history:
            self.history[ip] = []

# Stricter rate limiter for login attempts (anti-brute force: 10 attempts per minute)
login_rate_limiter = RateLimiter(requests_per_minute=10, burst_limit=5)
# General API rate limiter for public incident submissions (20 reports per minute)
incident_rate_limiter = RateLimiter(requests_per_minute=20, burst_limit=8)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Injects production-grade HTTP security headers on all responses:
    - X-Frame-Options: DENY (anti-clickjacking)
    - X-Content-Type-Options: nosniff (anti-MIME sniffing)
    - Content-Security-Policy (CSP): Restricts script execution sources
    - Referrer-Policy: strict-origin-when-cross-origin
    - Permissions-Policy: camera=(), microphone=(), geolocation=()
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # 1. Anti-Clickjacking: prevent dashboard from being framed in malicious sites
        response.headers["X-Frame-Options"] = "DENY"

        # 2. Prevent browser MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # 3. Referrer privacy protection
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # 4. Strict Permissions Policy (restrict sensitive hardware)
        response.headers["Permissions-Policy"] = "geolocation=(self), microphone=(), camera=()"

        # 5. Content Security Policy (allow local scripts, inline styles, leaflet tiles, and audio contexts)
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://unpkg.com; "
            "img-src 'self' data: https://*.tile.openstreetmap.org https://unpkg.com https://images.unsplash.com; "
            "connect-src 'self' http://127.0.0.1:* ws://127.0.0.1:*; "
            "font-src 'self' https://fonts.gstatic.com; "
            "media-src 'self' blob:; "
            "object-src 'none'; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp

        return response
