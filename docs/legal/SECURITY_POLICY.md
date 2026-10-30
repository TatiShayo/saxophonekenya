# Security Policy & Vulnerability Disclosure

**Last Updated:** October 30, 2026  
**Scope:** SaxophoneKenya Codebase & Production Deployments

The developers of **SaxophoneKenya** take security seriously. We adhere to industry best practices, OWASP Top 10 mitigation patterns, and defensive programming.

---

## 1. Security Architecture & Controls

### A. Data Protection & Cryptography
- **In Transit:** All external and internal communications require HTTPS with TLS 1.3 (minimum TLS 1.2). Insecure HTTP is automatically redirected or rejected with HSTS.
- **At Rest:** Database volumes, backups, and file storage are encrypted with AES-256.
- **Secrets Management:** Zero secrets or API credentials are stored in git repositories. All keys are loaded strictly from environment variables or dedicated secret vaults.

### B. Input Validation & Injection Defense
- **SQL / Database:** 100% parameterized queries or type-safe ORMs (Prisma, Supabase PostgREST, SQLx). Zero string-interpolated query execution.
- **Validation:** Strict schema validation on all API endpoints (Zod, Pydantic, or native type guards).
- **Cross-Site Scripting (XSS):** Context-aware HTML escaping, Content Security Policy (CSP), and sanitized dangerouslySetInnerHTML implementations.

### C. Authentication & Authorization
- Password hashing using **Argon2id** or **bcrypt** (minimum 12 salt rounds).
- Short-lived JSON Web Tokens (JWT) with secure, HttpOnly, SameSite cookies.
- Row-Level Security (RLS) policies enforcing multi-tenant isolation at the database layer.

---

## 2. Vulnerability Disclosure & Safe Harbor Policy

We welcome security researchers who report vulnerabilities in good faith.

### A. Reporting a Vulnerability
If you discover a security vulnerability, **DO NOT open a public GitHub issue**. Instead, report it privately:
- **Email:** `security@saxophonekenya.dev` (or the contact listed in the project root)
- **Information to include:**
  - Description of the vulnerability and attack vector.
  - Step-by-step reproduction steps or Proof of Concept (PoC).
  - Assessment of potential impact.

### B. Safe Harbor Commitment
If you conduct security research in compliance with this policy:
- We will not pursue legal action against you under the **Kenya Computer Misuse and Cybercrimes Act, 2018** or international cybercrime statutes.
- We will work with you to understand and remediate the issue promptly.
- We acknowledge valid security reports upon remediation.

### C. Out of Scope
The following activities are strictly prohibited and do NOT qualify for safe harbor:
- Distributed Denial of Service (DDoS) testing.
- Social engineering, phishing, or physical attacks on team members.
- Exfiltration of private user data beyond what is strictly necessary to demonstrate a vulnerability.
