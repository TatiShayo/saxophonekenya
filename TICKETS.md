# TICKETS.md — Tracer-Bullet Vertical Slice Work Breakdown (Frederic Sax Ke)

## Tracer-Bullet Tickets

### TB-01: Baseline Audit & Git Repository Initialization
- **Blocked By**: None
- **What it delivers**: Clean Git repository tracking all website files, media assets, and utility scripts with proper `.gitignore` excluding temporary files and archives, establishing an immutable baseline.
- **Acceptance Criteria**:
  - `git status` reports clean working directory.
  - Initial commit created with descriptive message.
  - Large archives (`*.zip`) and temporary caches ignored.

---

### TB-02: Secret Scanning Preflight & Push Protection Verification
- **Blocked By**: TB-01
- **What it delivers**: Comprehensive secret scan across all files and scripts using the 9 canonical HERMES pattern detectors (Stripe live/test keys, OpenAI/Anthropic API tokens, GitHub personal access tokens, Resend keys, Highnote credentials).
- **Acceptance Criteria**:
  - Zero detected secrets or private tokens in any repository file.
  - Scan report verified with 0 violations.

---

### TB-03: Automation Script Sanitization & Selector Alignment
- **Blocked By**: TB-01
- **What it delivers**: Complete alignment of selector targets in `capture_all.py` with active `#calendar` and `#ratecard` sections.
- **Acceptance Criteria**:
  - `capture_all.py` targets only active sections.
  - All DOM selector targets in automation scripts resolve to active elements in `index.html`.
  - Zero stale selectors in capture scripts.

---

### TB-04: Hermetic Verification & Automated Test Suite Implementation
- **Blocked By**: TB-02, TB-03
- **What it delivers**: Standalone, hermetic Python automated test suite (`tests/test_frederic_sax_suite.py`) testing HTML DOM structure, asset existence, anchor link matching, calendar date algorithms, WhatsApp URI encoding, and form field synchronization.
- **Acceptance Criteria**:
  - Test suite executes without external package dependencies using standard Python library.
  - 100% of test cases pass with exit code 0.
  - Results logged to `TEST_RESULTS.json` and attested in `ATTESTATION.jsonl`.

---

### TB-05: Mobile Parity & Viewport Verification
- **Blocked By**: TB-04
- **What it delivers**: Verification of responsive design rules across desktop (1440px) and mobile (390px) viewports: touch target sizing, drawer menu toggle, horizontal overflow prevention, and fluid calendar grid layout.
- **Acceptance Criteria**:
  - Zero horizontal overflow (`body { overflow-x: hidden }`).
  - Mobile drawer links match desktop navigation links 1:1.
  - Calendar slots stack cleanly in single-column layout on small viewports.

---

### TB-06: HERMES v6 / v7 Operational Artifact Bus & Sweep Attestation
- **Blocked By**: TB-04, TB-05
- **What it delivers**: Full suite of HERMES operational artifacts (`PREFLIGHT.json`, `RUN_MANIFEST.json`, `TASK_LEDGER.json`, `FINDINGS.json`, `SWEEP_SUMMARY.md`) documenting the complete audit findings, test attestation, and production readiness scorecard.
- **Acceptance Criteria**:
  - All artifacts conform to HERMES v6 schemas.
  - Findings categorized by Severity, Confidence E0–E4, and Actionability P0–P4.
  - Master summary generated in `SWEEP_SUMMARY.md`.
