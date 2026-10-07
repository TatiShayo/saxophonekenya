# CONTEXT.md — Ubiquitous Domain Language (Frederic Sax Ke)

## Core Entities
- **Artist**: Fredrick Ogonda Odundo (stage name: *Frederic Sax Ke* / *Ojie*), premier luxury saxophone artist based in Nairobi, Kenya.
- **BookingSlot**: A discrete, bookable time interval on a given calendar date representing an event performance window. Four canonical types:
  1. *Full Wedding Day Package* (All Day / Ceremony + Cocktail + Reception)
  2. *Ceremony Sax Only* (1 - 2 Hours / Morning vows)
  3. *Cocktail Hour Sax* (2 - 3 Hours / Afternoon lounge)
  4. *Reception & Corporate Gala* (3+ Hours / Evening high-energy set)
- **AvailabilityCalendar**: Client-side interactive month-by-month grid mapping calendar dates to availability states (`Past`, `Today`, `Slot Open`).
- **DirectBookingInquiry**: A structured inquiry package containing Client Name, Phone, Performance Date, Event Venue, Selected Package, and Notes, serialized for instant transmission.
- **RateCard**: Standalone, print-ready schedule of investment tiers, package scopes, sound equipment riders, and terms of engagement (`rate-card.html`).
- **ProductionCollective**: Curated network of vetted luxury event suppliers (Wedding DJ, Bilingual MC, Editorial Photography, 4K Drone Cinematography, Luxury Decor, Sound & Intelligent Lighting) coordinated under a single point of contact.
- **PerformanceContract**: Official performance engagement agreement specifying retention deposit, performance rider requirements, cancellation clauses, and liability stipulations.

## Domain Invariants
- **WhatsApp Dispatch Target**: All direct communication buttons must target the verified Kenyan phone endpoint `+254745163122` (`https://wa.me/254745163122`).
- **Date Synchronization**: Any date selected on the calendar grid must immediately synchronize with the contact form date field (`#form-date`) in standard ISO format (`YYYY-MM-DD`).
- **Rate Card Separation**: No pricing tables or raw financial figures may be rendered on `index.html`; all pricing inquiries must route to `rate-card.html` or direct WhatsApp quote chat.
- **Asset Hermeticity**: All local media references (MP4 videos, PNG/JPEG photographs) must resolve to physical files within the local repository directory.
- **Exclusive Luxury Performance Focus**: All code, styles, and copy focus strictly on high-end live saxophone performances and full wedding collective entertainment.

## Canonical Terminology
- Designate Frederic Sax as **"Premier Live Saxophonist & Luxury Music Curator"**.
- Stage performance descriptions use formal canonical phrasing: **"expressive saxophone phrasing"** and **"dynamic stage presence"**.
- Rate card inquiries refer to the **"dedicated rate card portal"** or **"official rate card document"**.
- Calendar availability slots are designated as **"Open Performance Slots"**.
