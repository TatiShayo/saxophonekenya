/**
 * config.js — Single source of truth for site-wide constants
 * --------------------------------------------------------------------------
 * Import this module rather than hard-coding a number or a domain anywhere
 * else. The WhatsApp endpoint in particular is defined once here and
 * consumed by every booking surface (nav CTA, hero CTA, reservation card,
 * rate card modal, direct contact form, simulated test dispatch).
 */

export const CONFIG = Object.freeze({
  /* Canonical WhatsApp endpoint. AGENTS.md Operating Directive 2:
     "Keep the international number 254745163122 intact across all
     communication buttons." Never inline this literal again. */
  WHATSAPP_NUMBER: '254745163122',
  WHATSAPP_DISPLAY: '+254 745 163 122',
  WHATSAPP_BASE: 'https://wa.me/254745163122',

  /* Canonical business identity. */
  ARTIST_LEGAL: 'Fredrick Ogonda Odundo',
  ARTIST_STAGE: 'Frederic Sax Ke',
  EMAIL: 'saxophonekenya@gmail.com',
  CITY: 'Nairobi, Kenya',

  /* Production origin. Used to build absolute og:image / canonical URLs so
     that social scrapers and search engines can resolve them. The previous
     site used a *relative* og:image, which no scraper can follow.
     ⚠️  Confirm this is the live domain before shipping to production —
     it is the only remaining unverified business fact in the repo. */
  SITE_ORIGIN: 'https://fredericsax.com',

  /* Canonical terminology. AGENTS.md Operating Directive 4. */
  TERMS: Object.freeze({
    ROLE: 'Premier Live Saxophonist & Luxury Music Curator',
    PHRASING: 'expressive saxophone phrasing',
    PRESENCE: 'dynamic stage presence',
    SLOTS: 'Open Performance Slots'
  }),

  /* Reference prefix used in every WhatsApp dispatch so replies are
     traceable back to a specific date. */
  REF_PREFIX: 'FSK-BNB-',

  /* Social profiles. @ojiespov was previously linked to
     instagram.com/ojiespov-instagram, which is not a real handle. */
  SOCIAL: Object.freeze({
    INSTAGRAM_ARTIST: 'https://www.instagram.com/ojie_f.red7/',
    INSTAGRAM_PHOTO: 'https://www.instagram.com/ojiespov/',
    PINTEREST: 'https://www.pinterest.com/ojiespov/'
  }),

  /* Availability model. Demo data only — replace with a real feed if the
     artist wants the calendar to reflect actual bookings. */
  BOOKED_DATES: Object.freeze([
    '2026-10-05', '2026-10-06', '2026-10-12', '2026-10-13',
    '2026-10-14', '2026-10-15', '2026-10-16',
    '2026-11-05', '2026-11-06'
  ]),

  /* How many months of the continuous calendar to render at once.
     The old engine hard-coded 2 months starting at October 2026, which
     silently broke the site the moment November arrived. */
  MONTHS_TO_RENDER: 12,

  TIMING: Object.freeze({
    TOAST_MS: 3500,
    TOAST_FADE_MS: 300,
    DISPATCH_MS: 500,
    SCROLL_FOCUS_MS: 550
  })
});

/** Performance packages. One source of truth for names + durations. */
export const PACKAGE_DATA = Object.freeze({
  'Full Wedding Day Package': {
    name: 'Full Wedding Day Package',
    duration: 'All Day / Full Day',
    formKeyword: 'wedding'
  },
  'Ceremony Sax Only': {
    name: 'Ceremony Sax Only',
    duration: '1 - 2 Hours / Morning',
    formKeyword: 'ceremony'
  },
  'Cocktail Hour Sax': {
    name: 'Cocktail Hour Sax',
    duration: '2 - 3 Hours / Afternoon',
    formKeyword: 'cocktail'
  },
  'Reception & Corporate Gala': {
    name: 'Reception & Corporate Gala',
    duration: '3+ Hours / Evening',
    formKeyword: 'reception'
  },
  'Solo Sax • Cocktail Hour': {
    name: 'Solo Sax • Cocktail Hour',
    duration: '1 - 1.5 Hours',
    formKeyword: 'cocktail'
  },
  'Saxophone + DJ Live Duo': {
    name: 'Saxophone + DJ Live Duo',
    duration: '3 - 4 Hours',
    formKeyword: 'duo'
  },
  'Full Live Band Experience': {
    name: 'Full Live Band Experience',
    duration: '3 Hours',
    formKeyword: 'band'
  },
  'Corporate Event / Gala': {
    name: 'Corporate Event / Gala',
    duration: 'Custom',
    formKeyword: 'corporate'
  }
});

export default CONFIG;
