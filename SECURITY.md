# Security Policy

## 1. Scope & Commitment
The Frederic Sax Ke / SaxophoneKenya production web platform (`https://saxophonekenya.com`) is committed to the highest standards of digital security, client confidentiality, and data integrity under the Kenya Data Protection Act, 2019 and international OWASP security baselines.

## 2. Reporting Security Vulnerabilities
If you discover a potential security vulnerability or misconfiguration, we appreciate your responsible disclosure.
- **Reporting Email:** `Tatibaraka@gmail.com` (or `security@saxophonekenya.com`)
- **PGP/Encrypted:** Available upon request.
- **Acknowledgment:** We acknowledge receipt of vulnerability reports within 24 hours.
- **Resolution Timeline:** Critical issues are triaged and patched within 72 hours.
- **Safe Harbor:** We will not pursue legal action against security researchers who report vulnerabilities responsibly, do not exploit vulnerabilities maliciously, do not access customer personal data without authorization, and give us a reasonable window to remediate before public disclosure.

## 3. Defense-in-Depth Security Controls

### A. HTTP Security Headers
Every edge response served via Vercel Edge (`vercel.json`) and Apache/cPanel (`.htaccess`) includes:
- **Content-Security-Policy (CSP):** Strict allowlist preventing unauthorized script execution, iframe clickjacking, and unsafe resources.
- **Strict-Transport-Security (HSTS):** `max-age=63072000; includeSubDomains; preload` enforcing HTTPS-only transport.
- **X-Frame-Options:** `DENY` to eliminate UI redressing and clickjacking.
- **X-Content-Type-Options:** `nosniff` preventing MIME-type sniffing attacks.
- **Referrer-Policy:** `strict-origin-when-cross-origin` preventing referrer leakage.
- **Permissions-Policy:** Strict hardware sandbox (`camera=(), microphone=(), geolocation=(), payment=()`).

### B. Secrets and Credentials Hygiene
- **Zero Secrets in Code:** Zero API keys, database credentials, or secret tokens reside in client-facing code, markup, or git repository history.
- **Environment Isolation:** All configuration parameters use scoped environment variables, with `.env*` strictly gitignored.
- **Automated Scanning:** Secret scans run automatically across git history to ensure continuous hygiene.

### C. Input Validation and XSS Defense
- **Serverless Sanitization:** All user-facing contact forms validate and sanitize input against XSS, SQL injection, and path traversal patterns.
- **Contextual Encoding:** Dynamic data rendered in DOM elements utilizes textContent encoding rather than unsafe innerHTML.

### D. Third-Party Supply Chain
- Automated vulnerability scanning enabled via GitHub Dependabot (`.github/dependabot.yml`).
- Subresource integrity and pin-to-SHA workflows for CI/CD actions.
