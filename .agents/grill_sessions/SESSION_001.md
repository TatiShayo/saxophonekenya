# Grilling Session 001: frederic-sax-ke (Frederic Sax Ke Luxury Showcase)
**Archetype**: Bespoke Luxury Creative Portfolio & Dynamic Booking Client
**Human Domain Authority**: Antigravity Lead Architect / Frederic Sax Ke Management
**Methodology**: Matt Pocock Agent Skills (/grilling + /grill-with-docs)
**Status**: FRONTIER EXHAUSTED — SHARED UNDERSTANDING ATTAINED

---

## Round 1: Core Architecture & Invariant Frontier

❓ **Q1** - **Booking Dispatch Pipeline & Infrastructure Footprint**: Should performance inquiries be routed through a backend transactional database (e.g., Supabase / PostgreSQL) or dispatched via client-side URI protocol handlers directly into WhatsApp?
➡️ *Recommendation*: In Kenya and the luxury private events market across East Africa, client direct conversion happens via WhatsApp. B2C clients demand immediate real-time response from the artist or management. A static client dispatch directly to `https://wa.me/254745163122` with URL-encoded dates and package choices eliminates backend operational overhead, guarantees zero server maintenance, and maximizes lead conversion velocity.

**Architect Decision**: APPROVED. WhatsApp direct link dispatch with pre-filled message syntax (`wa.me/254745163122?text=...`) is the primary conversion channel. The direct contact form acts as an on-page fallback that formats and transfers inquiries to the same WhatsApp endpoint.

---

❓ **Q2** - **Availability Calendar Invariants & State Synchronization**: How should the live availability calendar operate given that the artist does not run a public Cal.com or Google Calendar OAuth integration?
➡️ *Recommendation*: Provide a free, month-by-month browser-rendered calendar with date math supporting past, current, and future years. Past dates must be visually subdued with a "Past" label. Today must be highlighted. All future dates render as active booking candidates (`● Slot Open`). When any date is selected:
1. The calendar cell receives active golden glow focus (`.cal-selected`).
2. The dynamic slot panel opens with 4 distinct performance slots (Full Wedding Day, Ceremony Sax, Cocktail Hour Sax, Reception & Corporate Gala).
3. The selected ISO date (`YYYY-MM-DD`) synchronizes automatically into the `#form-date` input.
4. One-click WhatsApp button updates dynamically with the exact selected date and slot.

**Architect Decision**: APPROVED. The calendar state machine must run purely client-side with zero external calendar dependencies, accurately calculating monthly day offsets and leap years.

---

❓ **Q3** - **Rate Card Confidentiality & Portal Routing**: How should artist pricing and package investments be presented to prospective clients and wedding planners?
➡️ *Recommendation*: Do not embed sensitive pricing matrices directly on the hero or main landing flow. Isolate the complete investment schedule into a dedicated, printable standalone page (`rate-card.html`). On `index.html`, display a curated "Request Rate Card" gateway panel that explains what is included (Solo Sax, Sax + DJ Duo, Full Wedding, Live Band, KES & USD rates) and provides an explicit redirect button (`target="_blank"`) to `rate-card.html`.

**Architect Decision**: APPROVED. Hard separation between promotional showcase (`index.html`) and official rate card (`rate-card.html`) prevents landing page clutter and allows standalone sharing/printing of rates.

---

## Round 2: Edge Cases & Failure Modes Frontier

❓ **Q4** - **Media Delivery & Mobile Hero Video Optimization**: Large 4K/HD video backgrounds (`IMG_3610.MP4`, `IMG_3615.MP4`) can cause mobile bandwidth throttling and auto-play rejections. What is the fallback invariant?
➡️ *Recommendation*: Configure `<video>` elements with `autoplay muted loop playsinline` attributes, accompanied by high-resolution static poster frames (`poster="IMG_3609.PNG"`). Include an audio toggle button with visual feedback so users can unmute on demand.

**Architect Decision**: APPROVED. Muted autoplay with explicit poster fallbacks ensures zero layout shifts and instant hero rendering across iOS Safari and Android Chrome.

---

❓ **Q5** - **Brand Scope & Content Governance Rules**: What are the strict boundaries regarding brand focus and language conventions?
➡️ *Recommendation*:
1. Enforce strict brand purity: All navigation, body markup, CSS classes, and metadata focus 100% exclusively on Frederic Sax Ke live music performances and wedding entertainment.
2. Maintain formal copy governance: Reject cliché terminology in favor of formal, professional phrasing such as "expressive saxophone phrasing" and "dynamic stage presence".
3. Verify that all auxiliary scripts (such as screenshot automation) only target active DOM IDs (`#home`, `#bio`, `#videos`, `#calendar`, `#weddings`, `#ratecard`, `#pinterest`, `#portal`, `#contact`).

**Architect Decision**: APPROVED. The site maintains pure, undivided focus on Frederic Sax Ke live performances. Automated regression tests verify brand purity.

---

## Final Alignment Attestation
The design tree has been thoroughly walked down to all leaf nodes.
No silent assumptions remain regarding booking architecture, calendar state invariants, rate card routing, or content boundaries.
