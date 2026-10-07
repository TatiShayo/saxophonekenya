# ADR 0001: Static Luxury Web Architecture & Client-Side Booking Engine

## Status
Accepted

## Context
Frederic Sax Ke requires a digital presence representing his brand as a luxury event saxophone artist in Nairobi, Kenya. The client base includes high-net-worth couples, wedding planners, corporate gala organizers, and luxury venue directors.
Key technical constraints and user preferences identified during initial and follow-up sessions:
1. Fast mobile loading across cellular networks in Nairobi (Safaricom 4G/5G).
2. Frictionless booking inquiries: In Kenya, luxury clients convert predominantly via WhatsApp rather than email ticket queues.
3. Interactive availability browsing without maintaining paid third-party scheduling SaaS (e.g. Calendly, Cal.com).
4. Confidential investment pricing separated from public social media browsing.
5. Zero server hosting maintenance, zero backend database vulnerabilities, and 100% uptime.

## Decision
We chose a high-performance, purely client-side static web application architecture:
1. **Single-Page Showcase (`index.html`)**: Built with semantic HTML5, modern vanilla CSS3 (CSS custom properties, glassmorphism, responsive CSS Grid/Flexbox), and vanilla JavaScript.
2. **Client-Side Availability Calendar**: A month-by-month state machine calculating days in month, leap years, and weekday offsets in vanilla JS. Future dates render as interactive booking candidates that dynamically populate the booking slot panel and auto-sync with the contact form date.
3. **WhatsApp URI Protocol Routing**: Direct integration with WhatsApp Web/Mobile API (`https://wa.me/254745163122?text=...`) using pre-formatted, URI-encoded inquiry messages containing the chosen date and slot.
4. **Standalone Rate Card Portal (`rate-card.html`)**: Separation of detailed investment tiers into a standalone, print-optimized HTML document accessible via explicit CTA and secured with `noindex, nofollow` meta tags.
5. **Print-Ready Performance Contracts & Invoices**: Native browser print stylesheet (`window.print()`) in `#portal` for instant PDF generation of performance riders and contracts.

## Consequences
- **Positive**:
  - Sub-second first contentful paint (FCP) and zero server runtime costs.
  - Complete elimination of backend vulnerability attack surfaces (no SQL injection, no auth bypass, no SSRF).
  - High conversion rate through native WhatsApp deep-links matching Kenyan client behavior.
  - Zero external JavaScript library dependencies (no jQuery, no React overhead).
- **Negative / Trade-offs**:
  - Calendar availability operates on an inquiry model (client requests slot via WhatsApp, artist confirms offline) rather than automatic two-way calendar synchronization.
  - Rate card access control relies on page decoupling rather than authenticated user logins.
