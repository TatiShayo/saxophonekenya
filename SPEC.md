# SPEC 001: Frederic Sax Ke Luxury Showcase & Interactive Booking Engine

## Problem Statement
High-net-worth event hosts, brides, corporate event organizers, and festival directors in Nairobi and across East Africa need a fast, visually stunning, and responsive digital portal to experience Frederic Sax Ke's artistry, evaluate live stage recordings, browse monthly date availability, review wedding production packages, inspect contracts, and book performance dates with zero booking friction.

## Solution
A bespoke, dark-themed luxury web application implementing an Obsidian Black and Sandstone Camel visual design language. The platform combines background video performance reels, an interactive month-by-month availability calendar with time slot selection, a 1-click WhatsApp booking dispatch engine, a standalone rate card portal, a wedding production collective roster, and print-ready contract generators.

## User Stories
1. As a bride planning a wedding in Karen or Naivasha, I want to watch high-definition video excerpts of Frederic's saxophone performances, so that I can evaluate his sound, tone, and stage energy.
2. As an event host, I want to browse an interactive month-by-month calendar, so that I can check if my desired event date is open for booking.
3. As a prospective client, I want to click any available date on the calendar and see selectable performance slots (Full Wedding Day, Ceremony Sax, Cocktail Hour, Reception), so that I can tailor the booking to my specific timeline.
4. As a mobile client, I want to tap a single button to launch WhatsApp with my selected date and package pre-composed, so that I can communicate directly with Frederic or his management instantly.
5. As a client preferring a written form, I want clicking a calendar date to automatically populate the date input in the booking form, so that I do not have to type the date manually.
6. As a corporate event manager, I want to view a dedicated rate card page (`rate-card.html`) with transparent solo, duo, and full-band rates, so that I can prepare my event budget.
7. As an event planner, I want to review the Full Wedding Production Collective (DJ, MC, Photography, Cinematography, Decor, Sound & Lighting), so that I can contract a complete entertainment team under a single contact.
8. As a corporate client needing formal paperwork, I want to view and print sample performance contracts and custom invoices directly from the portal, so that procurement and legal terms are transparent.
9. As a mobile phone visitor, I want a hamburger drawer menu that lets me navigate smoothly to any section of the website without page reloads.
10. As a visitor browsing on cellular data, I want background video playback to be muted by default with an explicit unmute toggle, so that my device audio is not interrupted unexpectedly.
11. As a social media follower, I want direct links to Frederic's official Instagram profiles (`@ojie_f.red7` and `@ojiespov`), so that I can follow his daily lifestyle and visual aesthetic.
12. As a client who received a rate card link, I want the rate card page to have a print button that reformats the investment matrix into a clean, physical A4 PDF, so that I can share it with stakeholders.
13. As the website administrator, I want exclusive, unified brand focus on Frederic Sax Ke live saxophone and event entertainment services.
14. As a user on any screen size (from 375px mobile phones to 4K ultra-wide monitors), I want all cards, grids, buttons, and typography to remain legible, thumb-friendly, and visually harmonious.

## Implementation Decisions
- **Color Palette & Design System**:
  - Base: Obsidian Black (`#08070a`), elevated card backgrounds (`rgba(19, 17, 24, 0.88)`), glassmorphism overlay (`backdrop-filter: blur(24px)`).
  - Accents: Sandstone Camel (`#d4b28c`), Cashmere Champagne (`#f3e5d3`), Teakwood Bronze (`#b38b5d`), Gold glow (`rgba(212, 178, 140, 0.22)`).
  - Typography: `Cinzel` for luxury serif display headings, `Plus Jakarta Sans` for clean body copy, `JetBrains Mono` for metadata and badges.
- **Calendar Engine Architecture**:
  - Pure JavaScript state variables: `calCurrentYear`, `calCurrentMonth`, `calSelectedDate`, `calSelectedSlot`.
  - Date rendering function `renderMonthCalendar(year, month)` that builds 7-column grid (`SUN` through `SAT`).
  - Correct weekday offset calculation and days-in-month determination with February leap year support.
  - Active cell styling via `.cal-selected` class; past day disabling via `.past` class.
- **WhatsApp Dispatch Protocol**:
  - Format: `https://wa.me/254745163122?text=<ENCODED_MESSAGE>`.
  - Standardized message templates for calendar booking, hero CTA, rate card inquiry, and direct booking form.
- **Rate Card Architecture**:
  - Independent HTML document `rate-card.html` with dedicated CSS and print styles.
  - `#ratecard` section on `index.html` acts as a feature summary and redirect gateway (`target="_blank"`).
- **Print Optimization**:
  - CSS `@media print` rules hiding navigation bars, sticky CTA buttons, and background gradients, formatting contracts and rate sheets in clean black-and-white print typography.

## Testing Decisions
- **Seam**: Hermetic Python Test Suite (`tests/test_frederic_sax_suite.py`).
- Validate complete DOM document structure, meta tags, and open graph markup.
- Verify 100% physical existence of all locally referenced media assets (images, videos, posters).
- Verify bidirectional navbar and mobile drawer anchor routing against section IDs.
- Test calendar date math across leap years (2024, 2028), non-leap years (2025, 2026), and month transitions (December to January).
- Validate WhatsApp URL syntax and Kenyan telephone number normalization (`254745163122`).
- Verify complete brand cleanliness and exclusive focus on live performance services.
