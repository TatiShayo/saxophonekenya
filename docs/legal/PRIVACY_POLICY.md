# Privacy Policy

**Last Updated:** October 30, 2026  
**Effective Date:** October 30, 2026  
**Regulatory Compliance:** Kenya Data Protection Act, 2019 (Act No. 24 of 2019) | EU GDPR | California Consumer Privacy Act (CCPA/CPRA)

This Privacy Policy explains how **SaxophoneKenya** ("we", "us", or "our") collects, uses, processes, stores, and protects personal data when you use our software and services.

We operate under the fundamental principle of **data minimization** (collecting only the minimum data required to deliver core functionality) and **zero monetization of personal data** (we never sell your personal information).

---

## 1. Compliance with the Kenya Data Protection Act, 2019
We process all personal data in strict compliance with the principles set out in **Sections 25 and 26 of the Kenya Data Protection Act, 2019**:
- **Lawfulness, Fairness & Transparency:** Data is processed lawfully with your explicit consent or under clear contractual necessity.
- **Purpose Limitation:** Data is collected for specific, explicit, and legitimate operational purposes.
- **Data Minimization:** We restrict data collection strictly to what is adequate, relevant, and necessary.
- **Accuracy:** Reasonable steps are taken to ensure personal data is accurate and kept up to date.
- **Storage Limitation:** Personal data is retained only for as long as necessary to fulfill the stated operational purpose.
- **Integrity & Confidentiality:** Technical and organizational security safeguards prevent unauthorized disclosure or compromise.

---

## 2. Categories of Data Collected

| Category | Specific Elements | Lawful Basis for Processing | Retention Schedule |
| :--- | :--- | :--- | :--- |
| **Account Identity** | Email address, name, username, authentication token | Contractual necessity (account creation & auth) | Maintained while account is active; deleted within 30 days of closure |
| **Operational Data** | Application records, transactions, logs, preferences | Contractual necessity & core product operation | Retained per user configuration or automatically archived |
| **Telemetry & Diagnostics** | Pseudonymized error reports, system latency, HTTP status | Legitimate interest (debugging, security, reliability) | Scrubbed of PII; rotated after 90 days |
| **Billing Metadata** | Stripe/payment processor customer ID, transaction status | Legal compliance (tax & accounting records) | 7 years per statutory tax requirements (no card numbers stored) |

---

## 3. Third-Party Subprocessors
To operate cloud infrastructure, SaxophoneKenya utilizes industry-leading subprocessors bound by strict Data Processing Agreements:

| Subprocessor | Role | Data Handled | Location |
| :--- | :--- | :--- | :--- |
| **Supabase Inc.** | Encrypted database & auth hosting | User accounts, relational data | Global / US East (AES-256) |
| **Stripe Inc.** | Payment processing & fraud detection | Checkout tokens, billing history | USA / Global (PCI-DSS Level 1) |
| **Vercel Inc. / Cloudflare** | Edge routing & frontend hosting | Request IP, cache, SSL termination | Global Edge Network |
| **AI Providers (Anthropic / OpenAI / Google)** | Algorithmic processing (where applicable) | Ephemeral query payloads only (zero training retention) | USA (Encrypted in transit) |

---

## 4. International Cross-Border Data Transfers
Where personal data is transferred across borders (e.g. from Kenya to cloud data centers in the European Union or United States), such transfers comply with **Section 48 of the Kenya Data Protection Act** by ensuring:
1. Appropriate contractual clauses and technical safeguards (AES-256 encryption at rest, TLS 1.3 in transit).
2. Processing only by jurisdictions or providers offering equivalent or higher privacy protections.

---

## 5. Your Legal Rights as a Data Subject
Under the **Kenya Data Protection Act (Sections 26–36)** and international privacy frameworks, you have the right to:
1. **Right of Access:** Request confirmation of whether we process your personal data and obtain a copy.
2. **Right to Rectification:** Request correction of inaccurate or incomplete records.
3. **Right to Erasure ("Right to be Forgotten"):** Request permanent deletion of your data when no longer needed.
4. **Right to Data Portability:** Receive your data in a structured, machine-readable format (JSON or CSV).
5. **Right to Object:** Object to processing based on legitimate interests or automated profiling.
6. **Right to Lodge a Complaint:** You have the right to lodge a formal complaint with the **Office of the Data Protection Commissioner (ODPC) of Kenya** (Website: [www.odpc.go.ke](https://www.odpc.go.ke)).

To exercise any of these rights, email: `Tatibaraka@gmail.com`.

---

## 6. Security Safeguards
We implement defense-in-depth security:
- **Encryption:** All data in transit is protected using TLS 1.3. Persistent database tables are encrypted with AES-256.
- **Access Control:** Least-privilege role-based access control (RBAC) across all administrative boundaries.
- **Incident Response:** In the event of a confirmed data breach affecting personal data, we will notify affected users and the Kenya ODPC within seventy-two (72) hours of becoming aware of the breach, as mandated by law.

---

## 7. Policy Updates
We may update this Privacy Policy to reflect technical or regulatory changes. Updated versions will be published in this repository with an updated effective date.


## Statutory Registration Notice (Section 18)
Pursuant to Section 18 of the Kenya Data Protection Act, entities processing personal data in Kenya above statutory thresholds must maintain active registration with the Office of the Data Protection Commissioner (ODPC) (Website: www.odpc.go.ke). Contact: `Tatibaraka@gmail.com`.
