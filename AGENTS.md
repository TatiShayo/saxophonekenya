# AGENTS.md — Agent System Guide (Frederic Sax Ke)

## Repository Overview
- **Project**: Frederic Sax Ke Luxury Showcase & Booking Client
- **Version**: 3.0.0 (partial-based, modular, CSP-clean)
- **Tech Stack**: HTML5, Vanilla CSS3 (Custom Properties), Vanilla ES Modules, Python (build + tests)
- **Primary Entrypoint**: `index.html` — **generated** by `build.py` from `partials/`
- **Secondary Entrypoint**: `rate-card.html`
- **Local Dev Server**: `python serve.py 8080` (auto-builds, then serves http://localhost:8080)

## ⚠️ READ THIS FIRST — index.html IS GENERATED

```
partials/*.html  ──build.py──▶  index.html
```

**Never edit `index.html` directly.** It is a build artifact and any hand edit is destroyed the next time `build.py` runs (including automatically from `serve.py`). Edit the partial under `partials/` that owns the markup you want to change, then rebuild.

```bash
python build.py             # assemble + validate + write
python build.py --check     # validate only, write nothing
python build.py --stats     # report page weights
```

`build.py` fails the build if: a referenced asset is missing, an in-page anchor has no target, an element id is duplicated, a non-canonical WhatsApp number appears, an inline event handler is present, or a `{{TOKEN}}` is left unexpanded.

## Directory Map

```
SAX/SAX/
├── partials/            SOURCE — 14 HTML fragments (edit these)
│   ├── head.html          <head>: meta, OG, JSON-LD, font links, CSS links
│   ├── nav.html           skip link, toast host, live region, <nav>, mobile drawer
│   ├── hero.html          full-bleed video hero
│   ├── marquee.html       editorial strip
│   ├── bio.html           about the artist
│   ├── videos.html        live performance video theatre
│   ├── calendar.html      Airbnb-style booking calendar + reservation card + slot modal
│   ├── weddings.html      wedding packages + partners collective
│   ├── ratecard.html      rate card gateway section
│   ├── pinterest.html     moodboard
│   ├── portal.html        contract + invoice portal
│   ├── contact.html       direct booking form
│   ├── footer.html        footer
│   └── scripts.html       <noscript> + <script type=module>
│
├── css/                  DESIGN SYSTEM — load order matters
│   ├── tokens.css         every colour / type / radius / shadow / z-index
│   ├── base.css           reset, focus rings, skip link, reduced motion, a11y
│   ├── nav.css            navbar + mobile drawer + scroll-spy states
│   ├── hero.css           hero, marquee, immersive fixed background
│   ├── sections.css       section scaffolding + all content sections
│   ├── forms.css          form controls, validation, package chips
│   ├── booking.css        reservation widget, price breakdown
│   ├── airbnb-booking.css calendar grid, day cells, slot modal
│   ├── footer.css         footer
│   ├── rate-card.css      rate card document (loaded only by rate-card.html)
│   ├── print.css          A4 print output for contracts / invoices / rate card
│   └── responsive.css     breakpoints 1024 / 860 / 600 / 380 / 1600 / 2200
│
├── js/                   ES MODULES — loaded via <script type="module">
│   ├── config.js          ALL constants. The WhatsApp number lives here ONLY.
│   ├── utils.js           DOM helpers, date math, validation, openExternal()
│   ├── actions.js         central delegated handler for data-action
│   ├── toast.js           notification system (textContent only)
│   ├── nav.js             navbar, drawer, focus trap, scroll-spy
│   ├── hero.js            hero video, audio toggle, reduced motion
│   ├── videos.js          video theatre play affordance
│   ├── airbnb-calendar.js continuous calendar + reservation engine
│   ├── booking.js         package selection, form validation, WhatsApp dispatch
│   ├── portal.js          tabs, invoice generation, print isolation
│   ├── rate-card.js       currency switching, booking modal (code-split)
│   ├── fonts.js           non-render-blocking webfont activation
│   └── app.js             entry point: registers actions, boots every module
│
├── build.py              partial assembler + validator
├── optimise_media.py     video/image compression + evidence relocation
├── serve.py              dev server (auto-builds, binds 127.0.0.1)
├── tests/test_frederic_sax_suite.py   94 tests, must stay at 100%
├── build.config.json     {{SITE_ORIGIN}} / {{OG_IMAGE}} injection values
├── evidence/             QA screenshots (not deployed)
└── _media_backup/        pre-optimisation originals
```

## Operating Directives for Autonomous Agents

1. **Edit partials, never index.html.** Rebuild with `python build.py` after any change to `partials/`, `css/`, or `js/`.
2. **Zero external CSS/JS frameworks.** Pure vanilla. No build tooling beyond `build.py` (which is assembly, not transpilation), no Webpack/Vite/npm runtime dependencies.
3. **Strict WhatsApp endpoint.** `254745163122` is defined exactly once, in `js/config.js` as `CONFIG.WHATSAPP_BASE`. Every button imports it. Never inline the literal.
4. **No inline event handlers or inline `style` attributes.** New interactivity goes through `data-action="..."` in the partial plus a `registerAction()` call in `js/app.js`. This is what makes the Content-Security-Policy in `vercel.json` / `.htaccess` valid.
5. **Exclusive Brand Purity.** `king-sax.html` was deleted — it was a foreign-artist page that violated this directive. Do not reintroduce it.
6. **Formal Performance Phrasing.** Canonical terms: "expressive saxophone phrasing", "dynamic stage presence". Style the artist as "Premier Live Saxophonist & Luxury Music Curator".
7. **Rate Card Separation.** No pricing tables on `index.html`. All pricing routes to `rate-card.html` or WhatsApp.
8. **Always run the hermetic tests.** `python -m unittest tests.test_frederic_sax_suite` must report 100% before closing any ticket or proposing a merge.
9. **Asset Hermeticity.** All media must resolve to a physical file in the repository. `build.py` enforces this at build time; the test suite enforces it in CI.
10. **Do not add `X-XSS-Protection` back.** It is deprecated and actively discouraged. The CSP replaces it.

## Build Tokens

`partials/head.html` may contain these, expanded by `build.py` from `build.config.json`:

| Token | Source | Purpose |
|---|---|---|
| `{{SITE_ORIGIN}}` | `site_origin` | canonical URL, og:url, JSON-LD `@id` |
| `{{OG_IMAGE}}` | computed | absolute og:image / twitter:image |
| `{{FONT_URL}}` | `font_url` | Google Fonts request |
| `{{BUILD_DATE}}` | computed | build timestamp |

**Before production:** confirm `site_origin` in `build.config.json` is the real domain. It is currently `https://fredericsax.com`, taken from the previous codebase, and is the only unverified business fact left in the repo.

## Hosting Configuration — two files, must stay in sync

| Concern | Vercel | Apache / LiteSpeed |
|---|---|---|
| Routing, caching, headers | `vercel.json` | `.htaccess` |
| Security headers | both | both |
| Compression | automatic (Brotli/gzip) | `mod_deflate` / `mod_brotli` block |
| 404 page | `404.html` (automatic) | `ErrorDocument 404 /404.html` |
| Archived files blocked | n/a (curated deploy) | `<FilesMatch>` deny rule |

If you change a security header in one, change it in the other.

## Testing Decisions

The suite covers: document structure, CSP prerequisites, asset resolution, modular architecture, navigation integrity, accessibility, the calendar engine, WhatsApp/form integration, security, brand purity, the booking engine, print documents, and performance budgets. See `tests/test_frederic_sax_suite.py` — every test's docstring records the specific bug it prevents.


## Karpathy Engineering Directives (multica-ai/andrej-karpathy-skills)

To eliminate common agent coding pitfalls and over-engineering, every agent working in this repo must adhere to the 4 Karpathy Principles:

1. **Think Before Coding:**
   - Don\'t assume. Don\'t hide confusion. Surface tradeoffs and state assumptions explicitly.
   - If a simpler approach exists, say so. Push back when warranted.
2. **Simplicity First:**
   - Minimum code that solves the problem. Nothing speculative.
   - No features beyond what was asked. No abstractions for single-use code.
   - If you write 200 lines and it could be 50, rewrite it.
3. **Surgical Changes:**
   - Touch only what you must. Clean up only your own mess.
   - Match existing vanilla style and conventions. Do not refactor code that is not broken.
   - Every changed line must trace directly to the explicit request.
4. **Goal-Driven Execution:**
   - Define verifiable success criteria. Loop until verified.
   - Run python -m unittest tests.test_frederic_sax_suite (all 94 tests must pass) and python build.py --check before committing.
