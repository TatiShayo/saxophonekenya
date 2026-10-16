# Frederic Sax Ke — Full Site Audit & Rebuild Report

**Prepared:** 15 October 2026
**Repository:** `Website Antigravity/SAX/SAX/`
**Status:** Complete. 94/94 tests passing. Site live at http://localhost:8080
**Scope:** Security · Architecture · Performance · Accessibility · SEO · Correctness · Reactivity

---

## 1. Executive summary

The site was a single 3,622-line `index.html` carrying a 2,270-line inline `<style>` block
and ~450 lines of inline `<script>`, plus 95.7 MB of media from which no file had ever been
optimised. It worked, but it had 12 material defects — including three that would have caused
visible breakage — and it was structurally incapable of accepting a Content-Security-Policy.

It is now a partial-based, modular, CSP-clean application assembled by a build script, with
the media payload cut by 74%.

| Metric | Before | After |
|---|---|---|
| `index.html` | 3,622 lines · 147 KB | **1,295 lines · 68.7 KB** |
| Inline `<style>` block | 2,270 lines | **0** |
| Inline `<script>` block | ~450 lines | **0** |
| Inline `onclick` handlers | 49 (34 index + 15 rate card) | **0** |
| Inline `style=""` attributes | 25 (9 index + 16 rate card) | **0** |
| `.innerHTML` XSS sinks | 4 | **0** (all remaining are static) |
| CSS organisation | 1 block + 1 file | **12 modules** |
| JS organisation | 1 block + 1 file | **13 ES modules** |
| HTML organisation | 1 monolith | **14 partials** |
| Site media | 76.3 MB referenced | **24.5 MB** |
| Hero video | 25.62 MB, `moov` at file end | **1.38 MB**, `+faststart` |
| Test suite | 31 tests | **94 tests** |
| Build validation | none | **6 automatic checks** |
| Dead files in deploy root | `king-sax.html` + 27 QA PNGs | **0** |

**Nothing outside `_media_backup/` was deleted without a backup being taken first.**

---

## 2. Architecture — the big change

### What it was

One file. Every style, every script, every markup section. To change a button colour you
scrolled past 2,200 lines of CSS in the same file you were editing the button in. There was
no way to cache CSS separately from HTML, no way to code-split, and no way to reason about
any part of it without loading all of it.

### What it is

```
partials/*.html  ──build.py──▶  index.html
```

**14 partials** — `head`, `nav`, `hero`, `marquee`, `bio`, `videos`, `calendar`, `weddings`,
`ratecard`, `pinterest`, `portal`, `contact`, `footer`, `scripts`. Each is a self-contained
fragment of markup. `build.py` assembles them, injects `{{TOKENS}}` from `build.config.json`,
validates, and writes `index.html`.

**12 CSS modules**, loaded in dependency order — `tokens.css` defines every custom property
that the other 11 consume, so nothing can be overridden downstream by accident.

**13 ES modules**, loaded as `<script type="module" src="js/app.js">`. Because modules are
deferred by default, that single change removed a render-blocking script from the critical
path. `js/rate-card.js` is **code-split**: it is only fetched when a visitor opens the pricing
page, so portfolio visitors never download it.

### Why the number now lives in one place

`js/config.js` holds `CONFIG.WHATSAPP_BASE = 'https://wa.me/254745163122'`. It used to be
written literally in about 30 places across two files. A test now asserts that exactly one
`.js` file contains the `wa.me` URL, and `build.py` fails the build if any other
`wa.me/<number>` appears in the output.

### The build script is a safety net, not a convenience

`build.py --check` fails if any of these is true:

1. a referenced asset does not exist on disk
2. an in-page anchor (`href="#x"`) has no matching element id
3. an element id is duplicated
4. a non-canonical WhatsApp number appears
5. an inline event handler is present
6. a `{{TOKEN}}` is left unexpanded

That last group caught real bugs during the rebuild — see §8.

---

## 3. Security

### 3.1 Cross-site scripting — 4 sinks removed

| Location | Was | Now |
|---|---|---|
| `showToast()` | `t.innerHTML = \`<span>&bull;</span> ${msg}\`` — reached with a **client name** from the invoice form, a **photo title** from the moodboard, and a **package name** | `el('span', { text: message })` → `textContent`. Markup in the message renders as literal characters |
| `king-sax.html` `showToast()` | Same pattern, reached from a `<input type=number>` value | **File deleted** |
| `generateInvoicePreview()` | Interpolated client name into innerHTML | `textContent` via `invoiceLine()` |
| `handleDirectBookingSubmit()` | Built a WhatsApp body from raw form values | `encodeURIComponent` + `textContent` |

A test (`test_no_innerhtml_sinks`) now fails the build if any `.innerHTML` assignment
contains `${` or reads `.value`.

### 3.2 Reverse tabnabbing — 4 windows fixed

Every outbound `window.open` shipped as `window.open(url, '_blank')` with no `noopener`, which
hands the opened document a live `window.opener` reference. All four now route through
`openExternal()` in `js/utils.js`:

```js
export function openExternal(url) {
  const win = window.open(url, '_blank', 'noopener,noreferrer');
  if (win) win.opener = null;
  return win;
}
```

The test suite additionally asserts that every `<a target="_blank">` in both documents carries
`rel="noopener"`.

### 3.3 Content-Security-Policy — now possible

The site could never accept a strict CSP because 49 inline `onclick` handlers and 25 inline
`style=""` attributes require `'unsafe-inline'` for both `script-src` and `style-src`.

All 74 are gone. Interactivity now runs through a central delegated handler in
`js/actions.js` keyed on `data-action` attributes, so the CSP can be:

```
script-src 'self'                       ← no unsafe-inline
style-src 'self' 'unsafe-inline'        ← one unavoidable exception, see below
```

`style-src` still permits `'unsafe-inline'` because a handful of one-off presentational rules
would need their own class each; the risk of style injection is far lower than script
injection, and this is documented as the remaining CSP gap. `'unsafe-eval'` is banned
outright.

### 3.4 Security headers — 7 added, 1 deprecated header removed

`vercel.json` and `.htaccess` now both set:

| Header | Why |
|---|---|
| `Content-Security-Policy` | the primary XSS defence |
| `Strict-Transport-Security` | `max-age=63072000; includeSubDomains; preload` |
| `X-Content-Type-Options: nosniff` | stops MIME sniffing |
| `X-Frame-Options: DENY` | clickjacking |
| `Referrer-Policy: strict-origin-when-cross-origin` | stops path leakage |
| `Permissions-Policy` | denies camera, mic, geolocation, payment, USB, FLoC |
| `Cross-Origin-Opener-Policy: same-origin` | isolates the browsing context |

**Removed:** `X-XSS-Protection: 1; mode=block`. It is deprecated — removed from Chrome and
Edge, retired from the spec, and actively discouraged because it can *introduce* issues in
legacy browsers. The CSP replaces it. A test asserts it never comes back.

### 3.5 The dev server was a network-exposed hole

`serve.py` bound `0.0.0.0` and sent `Access-Control-Allow-Origin: *`. On any shared or public
network that exposed the entire site *and* the two 82 MB deployment archives to every other
device on the LAN, with no authentication. It now binds `127.0.0.1` by default (`--host
0.0.0.0` must now be passed deliberately), sends no CORS header at all, and serves a custom
404 page instead of the plain-text default.

### 3.6 Deploy artefacts exposed

`.htaccess` has no access control, and `README_HOSTING.txt` instructs extracting the folder
straight into `public_html`. That folder contained two 82 MB `.zip` archives, which would have
become publicly downloadable. A `<FilesMatch>` rule now denies `.zip .py .pyc .jsonl .log .md
.sh .bak` and `build.py`, and `robots.txt` disallows them from crawling.

### 3.7 Secret scanning widened

The old scan only walked `.ts .tsx .js .json .py .html .md .env` — which silently skipped the
`.zip` archives, the `.jsonl` attestation logs, the `.txt` docs and every CSS file. Now
scanning covers all of those plus `.css .webmanifest .xml`. (No secrets were found; this was
a coverage gap, not a leak.)

---

## 4. Correctness — 12 real bugs

### 4.1 The calendar was hard-coded to October 2026 — **would break in production**

```js
viewYear: 2026,
viewMonth: 9,                    // October
today: new Date(2026, 9, 7),     // "today" is a fixed constant
rangeStart: new Date(2026, 9, 8),
rangeEnd: new Date(2026, 9, 10),
monthsCount: 2,                  // October and November only
```

Today is 15 October 2026. On 1 November, **every cell on screen becomes "past"**, the default
selection is an unavailable date, and the site has no way to reach December. The site has a
silent expiry date.

Fixed: `today` is now `startOfToday()`, the view anchors to the real current month, the
default selection is the first bookable day at or after today, and `MONTHS_TO_RENDER: 12`
gives a rolling year with PageUp/PageDown month navigation.

### 4.2 A booking range could span held dates

`handleDateClick` accepted any end date after the start. A guest could select 8–16 October
while the 12th, 13th, 14th, 15th and 16th were all in `bookedDates`. The WhatsApp message then
asked Frederic to confirm a week in which five days were unavailable.

Fixed with `rangeIsClean()`, which walks every day in the range and rejects the selection with
`"That range includes held dates. Please pick a clear run of days."`

### 4.3 The package you clicked was never the package you sent

`selectSlotType()` updated four DOM nodes. `dispatchAirbnbReservationWhatsApp()` read
`STATE.selectedSlot.package` — a variable that only `selectPerformanceSlot()` ever wrote. The
two never met.

Selecting **Ceremony Sax Only** and pressing Reserve sent **"Full Wedding Day Package"** to
WhatsApp, every single time.

Fixed: `setAirbnbReservationPackage()` is now the single write path, and `selectSlotType`
fires a `fsk:package-selected` event into it.

### 4.4 The "pick a date" button scrolled to a hidden element

```html
<div class="segmented-cell cell-date"
     onclick="document.getElementById('cal-grid').scrollIntoView({behavior:'smooth'})">
```

`#cal-grid` was `style="display:none"`. `scrollIntoView` on a `display:none` element does
nothing. The PERFORMANCE DATE cell in the reservation card was inert.

It is now a real `<button id="cal-pick-date-btn">` that scrolls to the calendar.

### 4.5 Two broken CSS custom properties

`--shadow-card` and `--font-body` were referenced but never defined anywhere:

```css
.calendar-wrapper-card  { box-shadow: var(--shadow-card); }   /* → invalid → no shadow */
.airbnb-amenities-card  { box-shadow: var(--shadow-card); }   /* → invalid → no shadow */
.btn-airbnb-reserve     { font-family: var(--font-body); }    /* → invalid → system font */
```

An undefined custom property makes the whole declaration invalid at computed-value time, so
two cards rendered with **no shadow at all** and the primary reserve button silently fell back
to a system font. Both are now defined in `tokens.css`. A test asserts no `var()` reference in
any stylesheet is undefined.

### 4.6 Anchor links landed under the fixed navbar

The nav is `position: fixed; height: 72px`. Sections had no `scroll-margin-top`, so every
anchor jump placed the section heading behind the navbar. Fixed with
`scroll-padding-top: calc(var(--nav-height) + 24px)` on `html`.

### 4.7 The UTC date bug that allowed past bookings

```js
const today = new Date().toISOString().split('T')[0];
dateInput.min = today;
```

`toISOString()` is UTC. For a visitor in East Africa (UTC+3) between 00:00 and 03:00 local
time this computes **yesterday**, so `min` permitted a past performance date. Replaced with
`formatISODate()`, which builds the string from local `getFullYear/getMonth/getDate`.

### 4.8 "Download Contract (PDF)" printed the whole page

`downloadSampleContract()` called `window.print()`. The visitor got the navbar, the hero video,
the marquee, the footer and the toast container on paper.

It now sets `body.printing-contract`, which lets `css/print.css` render **only** the contract:
everything else hidden, dark theme neutralised to black-on-white, `@page` margins set, table
headers repeated on page 2, interactive chrome removed, and link URLs printed in full. The
class resets on `afterprint` plus a 4-second safety net for browsers that never fire the event.

### 4.9 The invoice generator generated nothing

`generateInvoicePreview()` showed a toast saying an invoice had been created and produced no
invoice. It now renders a real document — reference number, client, date, package, investment
in both currencies, payment status, deposit terms, and the artist's contact block.

### 4.10 Five sources of truth for pricing

Prices existed in: the table's `data-kes`/`data-usd` attributes, the modal `<option>` data
attributes, the `PACKAGE_PRICES` JS object, a hardcoded duplicate array inside `setCurrency`,
and a fifth copy in the WhatsApp message builder. Any price change meant editing five places,
and they had already drifted.

Consolidated into a single `PACKAGE_PRICES` object in `js/rate-card.js`. The data attributes
remain as the HTML fallback, so the page renders correctly before the module boots.

### 4.11 A dead Instagram handle

`@ojiespov` was linked to `instagram.com/ojiespov-instagram` — not a real account. Both
Instagram links now point at real handles (`@ojie_f.red7` and `@ojiespov`), sourced from
`CONFIG.SOCIAL`.

### 4.12 Two duplicate calendar engines

`index.html` contained a complete month-grid calendar (`renderMonthCalendar`, `calPrevMonth`,
`calNextMonth`, `updateSlotPanel`, `PACKAGE_DATA`, ~90 lines of CSS) that rendered into
`#cal-grid` — a `display:none` container. It ran on every `DOMContentLoaded`, did work, and was
invisible. It has been removed; the Airbnb continuous stream is the single engine.

---

## 5. Performance

### 5.1 Media: 76.3 MB → 24.5 MB

| Asset | Before | After | How |
|---|---|---|---|
| `IMG_3610.MP4` (hero) | 25.62 MB | **1.38 MB** | H.264 CRF 28, 1080p cap, `+faststart`, mono 96k |
| `IMG_3615.MP4` | 22.63 MB | **6.19 MB** | same |
| `IMG_3617.MP4` | 6.09 MB | **1.84 MB** | same |
| `IMG_3618.MP4` | 7.02 MB | 7.02 MB | already efficient H.265 @ 576×1024 — re-encode was larger, so correctly left alone |
| `IMG_3612.PNG` | 7.13 MB | **1.69 MB** | downscaled to 1920px, PNG `compress_level=9` |
| `IMG_3611.PNG` | 1.77 MB | **1.68 MB** | optimised |
| `IMG_3608.PNG` | 1.23 MB | **1.16 MB** | optimised |
| `IMG_3613.PNG` | 2.14 MB | 2.14 MB | re-encode was larger, kept |
| `IMG_2259.jpg` | 1.45 MB | **0.23 MB** | progressive JPEG q82 |

`optimise_media.py` re-runs this any time new media arrives. Originals are preserved in
`_media_backup/`.

### 5.2 The hero video's `moov` atom was at the end of the file

The old `IMG_3610.MP4` had its `moov` atom at the end, so a browser could not begin playback
until the **entire 25.62 MB** had downloaded. It is the LCP element, so first paint waited on
it. The re-encode uses `-movflags +faststart`, which moves `moov` to the front — playback now
starts after the first few hundred KB.

### 5.3 Webfonts were render-blocking

Three families, fourteen weight variants, in a blocking `<link rel="stylesheet">`. The page
could not paint until Google Fonts responded.

Now shipped with `media="not all"` — the browser fetches it at low priority without blocking
paint — and `js/fonts.js` flips `media` to `'all'` once the module boots. A `<noscript>` block
loads it normally with JS disabled. No inline `onload` handler, so the CSP stays valid.

### 5.4 Zero lazy loading

The site had **no** `loading="lazy"` and no `decoding="async"` anywhere. All 8 images and all
4 videos downloaded on first paint.

Now: the hero poster is `fetchpriority="high"` (it *should* load first), the bio portrait is
eager, and everything else is `loading="lazy" decoding="async"` with explicit `width`/`height`
so no layout shift occurs. Videos below the fold get `preload="none"` via IntersectionObserver
until they scroll into view.

### 5.5 `background-attachment: fixed`

The immersive background on `.site-main-flow` used `background-attachment: fixed`. The
compositor cannot cache that layer, so it repaints the full-bleed image on every scroll frame —
the most expensive property in the stylesheet on mobile. It now switches to `scroll` below
1024px, which is visually indistinguishable at that size.

### 5.6 The remaining CSP gap

`style-src 'unsafe-inline'` is still required. This is the one deliberate exception; see §3.3.

---

## 6. Accessibility — 14 fixes

| Issue | Before | After |
|---|---|---|
| No skip link | none | `.skip-link`, first focusable element |
| Hamburger state unannounced | no `aria-expanded` | `aria-expanded` + `aria-controls`, animated to X |
| Drawer focus escaped | no trap, no Escape | Tab trap + Escape + outside-click + focus restore |
| Drawer links tabbable when closed | tabbable | `visibility:hidden` via `aria-hidden="true"` |
| Day cells unusable by keyboard | `<div onclick>` | `role="gridcell"`, `tabindex="0"`, arrows/Home/End/PageUp/PageDown/Enter |
| Slot modal not a dialog | class toggle only | `role="dialog"` + `aria-modal` + focus trap + Escape + restore |
| Package chips not controls | `<div onclick>` | `<button aria-pressed>` |
| Moodboard items not controls | `<div onclick>` | `<button>` |
| Clickable table rows not controls | `<tr onclick>` | `data-action` + `cursor:pointer` rule; keyboard users use the in-row button |
| Toasts not announced | visual only | container is `role="status" aria-live="polite"` |
| Sections unlabelled | bare `<section id>` | `aria-labelledby` pointing at the heading |
| Images without alt / dimensions | partial | all have alt + width + height |
| Inputs without labels | `<div class="label">` | `<label for>` on all 11 controls |
| Inputs without `autocomplete` | none | name, tel, organization where applicable |
| Contrast failure | `--text-dim: #6b6459` = **3.2:1** on `#08070a` | `#8b837a` = **≥5.0:1**, passes WCAG AA |

Also added: `:focus-visible` rings on every interactive element, `prefers-reduced-motion`
support that suppresses the hero video entirely, 44px minimum touch targets under
`pointer: coarse`, `forced-colors` support, and a `noscript` block telling JS-disabled visitors
to use WhatsApp.

---

## 7. SEO & discoverability

Added from nothing:

- `<link rel="canonical">` on both pages
- **Absolute** `og:image` — the old site had a *relative* `og:image`, which no social scraper
  can resolve, so every shared link rendered with no preview image
- `og:site_name`, `og:locale`, `og:type`, `og:url`, `twitter:card`, `twitter:title/description/image`
- `Musician` + `WebSite` JSON-LD: legal name, stage name, job title, address, telephone,
  email, genre, five `areaServed` countries, `sameAs` social profiles, and four priced `Offer`
  nodes (solo / cocktail / full wedding / gala)
- `sitemap.xml`, referenced from `robots.txt`
- `manifest.webmanifest` with shortcuts to Calendar, Rate card and WhatsApp
- `theme-color`, `color-scheme`
- A `404.html` with real navigation, wired up in `.htaccess`
- `robots.txt` now blocks `*.zip`, `partials/`, `build.py`, `build.config.json`

**One decision left to you:** `rate-card.html` carries `noindex`. I removed `nofollow` (it was
pointless) but kept `noindex`, because that gate on pricing is a deliberate business choice —
it means your rate card can never appear in search results, so it can only ever be a
send-only document. If you want it indexed, delete that one meta tag. I have not changed your
pricing visibility without telling you.

---

## 8. What the build validator caught

The new `build.py --check` found real problems in the freshly-written partials before they
ever reached a browser:

- `{{SITE_ORIGIN}}` left unexpanded in `head.html`
- `href="#bnb-calendar-stream"` resolved to nothing on one pass
- A duplicate `id="toast-container"` between `nav.html` and the build shell
- A duplicated `id="bnb-live-region"` from the same cause
- A `data-action="select-package"` with no registered handler, which would have been a
  silently dead button

Each was fixed at source. The suite now has a dedicated test
(`test_data_actions_are_registered`) that cross-references every `data-action` in the markup
against `registerAction()` calls, so this class of bug cannot regress.

---

## 9. Dead code and files removed

| File | Size | Why |
|---|---|---|
| `king-sax.html` | 92 KB | **A different artist.** "King Sax", album "ENERGY", Washington D.C., `kingsax.com`. Nothing linked to it, it was in neither deployment zip, no test covered it, and it directly violated `AGENTS.md` Directive 3 on brand purity. It also contained an `innerHTML` XSS sink fed by a form value |
| `IMG_2259.png` | 5.63 MB | Unreferenced by any page |
| `IMG_2259.HEIC` | 1.45 MB | Unreferenced, and unsupported by most browsers |
| `vest_crop.jpg` | 18 KB | Unreferenced |
| `shot_wardawear_preview.png` | 0.44 MB | A screenshot from a previous client; "wardawear" is on the test suite's own disallowed-token list |
| 27 QA screenshots | 21 MB | Moved to `evidence/`. Not referenced by any page, but not deleted either — `run_vitl.py` and the capture scripts can still use them |

`_media_backup/` holds the pre-optimisation originals of all 11 media files.
`_BACKUP_pre-refactor/` holds the complete pre-rebuild source tree.

---

## 10. Test suite: 31 → 94 tests

Every original assertion is preserved. Where an assertion referenced a string that only
existed in the old monolith — an inline handler, a hard-coded date — it was replaced by an
equivalent assertion against the module that now owns that behaviour.

New coverage:

- **CSP prerequisites** — zero inline handlers, zero inline `<style>`, zero `javascript:` URLs
- **No `innerHTML` sink** may interpolate `${` or read `.value`
- **No `window.open` without `noopener`**, comments stripped
- **The WhatsApp URL exists in exactly one module**
- **Every `data-action` has a registered handler**
- **No duplicate element ids** anywhere
- **Every anchor resolves to a real element id**
- **Every `url()` in every stylesheet resolves to a real file** — this is what would have
  caught the `IMG_2259.png` deletion before production
- **No undefined CSS custom property** is referenced
- **Rate-card CSS is not shipped to portfolio visitors**
- **All `<script>` tags are deferred modules** (ld+json excluded)
- **`X-XSS-Protection` is absent** from both header configs
- **Page-weight and line-count budgets** — the suite fails if `index.html` regresses past
  100 KB or 1,600 lines

```
Ran 94 tests in 25.092s
OK
```

---

## 11. How to work on this now

```bash
# 1. Edit a partial, never index.html
partials/calendar.html

# 2. Rebuild (serve.py does this automatically)
python build.py

# 3. Validate without writing
python build.py --check

# 4. Test
python -m unittest tests.test_frederic_sax_suite

# 5. Run
python serve.py 8080          # binds 127.0.0.1, auto-builds, then serves
```

`serve.py 8080` and `serve.py --port 8080` both work. Use `--host 0.0.0.0` only on a trusted
network — it exposes the whole folder.

---

## 12. Open items — decisions I did not make for you

1. **Confirm the domain.** `build.config.json` sets `site_origin` to `https://fredericsax.com`,
   taken from the previous codebase. It feeds `canonical`, `og:url`, `og:image`,
   `twitter:image` and every JSON-LD `@id`. **This is the only unverified business fact left in
   the repo.** Change it in one place before deploying, or every rich preview and canonical
   tag will point at the wrong host.

2. **Decide whether the rate card should be indexed.** See §7.

3. **`IMG_3618.MP4` is H.265.** It is already efficient and cannot be usefully re-encoded to
   H.264, but H.265 will not play in older Safari or any version of Internet Explorer. If you
   need maximum compatibility it needs a separate H.264 copy served via `<source>`.

4. **Booked dates are demo data.** `CONFIG.BOOKED_DATES` in `js/config.js` is nine hardcoded
   October/November dates. The calendar's *mechanics* are real; its *availability* is not.
   When you want the calendar to reflect actual bookings, this is the one value to replace.

5. **`style-src 'unsafe-inline'`.** The remaining CSP gap. Closing it means giving each of the
   ~8 leftover one-off presentational rules its own class.

6. **Cache policy is deliberately conservative.** Because filenames carry no content hash,
   `immutable` would be unsafe — a re-cropped image would never reach a returning visitor.
   Media is `max-age=604800, stale-while-revalidate=86400`; HTML is `must-revalidate`. If you
   ever add content-hashed filenames, switch media to `immutable` for the real win.

---

## 13. Verification performed

- `python -m unittest tests.test_frederic_sax_suite` — **94 passed, 0 failed**
- `python build.py --check` — clean
- `python build.py --stats` — reported
- HTTP probes against the running server: `/`, `/rate-card`, `/rate-card.html`,
  `/frederic-sax.html`, `/robots.txt`, `/sitemap.xml`, `/manifest.webmanifest`, `/404.html`,
  `/nope` (404 with the custom page)
- All 12 CSS files — HTTP 200, `Content-Type: text/css`
- All 13 JS modules — HTTP 200, `Content-Type: application/javascript` (this is what breaks
  ES modules when wrong)
- All media — HTTP 200 with correct `Content-Type`
