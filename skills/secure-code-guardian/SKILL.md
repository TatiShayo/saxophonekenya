---
name: secure-code-guardian
description: OWASP Top 10 Mitigator and Secure Code Guardian. Provides comprehensive defensive security guidelines, input sanitization rules, and vulnerability mitigation protocols.
---

# Secure Code Guardian & OWASP Top 10 Mitigator

## 1. Overview
The Secure Code Guardian enforces robust defensive coding principles, eliminating vulnerabilities in web applications across the OWASP Top 10 spectrum:
- A01: Broken Access Control
- A02: Cryptographic Failures
- A03: Injection (SQL, XSS, Command, SSRF)
- A04: Insecure Design
- A05: Security Misconfiguration
- A06: Vulnerable and Outdated Components
- A07: Identification and Authentication Failures
- A08: Software and Data Integrity Failures
- A09: Security Logging and Monitoring Failures
- A10: Server-Side Request Forgery (SSRF)

## 2. Mandatory Rules for Web & Frontend Applications

### A. Zero Secrets in Client Code
- Never expose API keys, bearer tokens, or database connection strings in client-facing HTML, CSS, JavaScript, or git history.
- Ensure all `.env*` files are strictly listed in `.gitignore`.
- Run automated secret scans across all commits before deployment.

### B. Security Headers Baseline
Every production HTTP response must enforce defensive headers:
- `Content-Security-Policy`: Restricts resource sources to prevent XSS and code injection.
- `Strict-Transport-Security`: Enforces TLS 1.3/HTTPS transport (`max-age=63072000; includeSubDomains; preload`).
- `X-Frame-Options: DENY`: Prevents UI redressing and clickjacking.
- `X-Content-Type-Options: nosniff`: Prevents MIME-type confusion attacks.
- `Referrer-Policy: strict-origin-when-cross-origin`: Restricts referrer headers to protect private query paths.
- `Permissions-Policy`: Restricts browser hardware access (`camera=(), microphone=(), geolocation=()`).

### C. Input Sanitization & DOM Safety
- Validate all user input server-side with strict schemas.
- Avoid using `innerHTML`, `document.write`, or `eval()` with user-supplied data; use `textContent` and `createElement()` instead.
- Contextually encode dynamic output to neutralize Cross-Site Scripting (XSS).

### D. Multi-Tenant & Data Isolation
- Enforce strict server-side authorization checks on all operations (prevent Insecure Direct Object References - IDOR).
- Verify user ownership of entities before read, update, or delete actions.
