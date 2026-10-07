# AGENTS.md — Agent System Guide (Frederic Sax Ke)

## Repository Overview
- **Project**: Frederic Sax Ke Luxury Showcase & Booking Client
- **Tech Stack**: HTML5, Vanilla CSS3 (Custom Properties & Glassmorphism), Vanilla JavaScript, Python (automation & testing)
- **Primary Entrypoint**: `index.html` (Main Portfolio & Booking Application)
- **Secondary Entrypoint**: `rate-card.html` (Standalone Official Rate Card)
- **Local Dev Server**: `python serve.py 8080` (runs at http://localhost:8080)

## Directory Map
- `index.html`: Complete single-page luxury showcase featuring Hero, Bio, Videos, Availability Calendar, Wedding Packages, Rate Card Gateway, Moodboard, Contracts/Invoice Portal, and Direct Booking Form.
- `rate-card.html`: Dedicated, printable rate card document with transparent pricing tiers and terms.
- `frederic-sax.html`: Meta refresh redirect page to `index.html`.
- `serve.py`: Threading HTTP server with no-cache and CORS headers.
- `capture_all.py`, `take_shots.py`, `take_mobile_shots.py`: Headless browser capture scripts for visual verification.
- `tests/`: Hermetic test suite (`test_frederic_sax_suite.py`).
- `.agents/`: Agent skills artifacts (`grill_sessions/SESSION_001.md`).
- `docs/adr/`: Architecture decision records.

## Operating Directives for Autonomous Agents
1. **Zero External CSS/JS Frameworks**: Maintain pure vanilla implementation. Do not introduce build tooling (Webpack, Vite, npm) unless explicitly instructed.
2. **Strict WhatsApp Endpoint**: Keep the international number `254745163122` intact across all communication buttons.
3. **Exclusive Brand Purity**: Ensure all visual and textual elements remain 100% focused on Frederic Sax Ke live performance and wedding entertainment.
4. **Formal Performance Phrasing**: Use canonical terms: "expressive saxophone phrasing" and "dynamic stage presence".
5. **Always Run Hermetic Tests**: Before closing any ticket or proposing a merge, run `python -m unittest tests/test_frederic_sax_suite.py` and ensure 100% pass rate.
