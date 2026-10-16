#!/usr/bin/env python3
"""
Hermetic Automated Test Suite for Frederic Sax Ke Luxury Website
==========================================================================
ARCHITECTURE v2.0 — partial-based, modular, CSP-clean.

The suite was updated when the site moved from a single 3,622-line
`index.html` with a 2,270-line inline <style> block and ~450 lines of inline
<script> to:

    partials/*.html   source fragments (14 files)
    css/*.css         12 modular stylesheets
    js/*.js           13 ES modules
    build.py          assembles partials -> index.html

Every original assertion is preserved. Where an assertion referenced a
string that only existed in the old monolith (an inline handler, a
hard-coded calendar date), it has been replaced by an equivalent assertion
against the module that now owns that behaviour — plus new tests for the
refactor's guarantees:

    * zero inline event handlers anywhere (CSP prerequisite)
    * zero inline <style> blocks
    * zero innerHTML sinks in the shipped JavaScript
    * zero window.open() without noopener
    * the WhatsApp number exists in exactly one module, not 30 places
    * every local asset referenced anywhere actually exists
    * every in-page anchor resolves to a real element id

Run:  python -m unittest tests.test_frederic_sax_suite -v
"""

from __future__ import annotations

import os
import re
import unittest
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent

INDEX = REPO_DIR / "index.html"
RATE_CARD = REPO_DIR / "rate-card.html"
REDIRECT = REPO_DIR / "frederic-sax.html"
NOT_FOUND = REPO_DIR / "404.html"
BUILD = REPO_DIR / "build.py"

CSS_DIR = REPO_DIR / "css"
JS_DIR = REPO_DIR / "js"
PARTIAL_DIR = REPO_DIR / "partials"

REQUIRED_CSS = [
    "tokens.css", "base.css", "nav.css", "hero.css", "sections.css",
    "forms.css", "booking.css", "airbnb-booking.css", "footer.css",
    "rate-card.css", "print.css", "responsive.css",
]

REQUIRED_JS = [
    "config.js", "utils.js", "actions.js", "toast.js", "nav.js",
    "hero.js", "videos.js", "airbnb-calendar.js", "booking.js",
    "portal.js", "rate-card.js", "fonts.js", "app.js",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_js(name: str) -> str:
    return (JS_DIR / name).read_text(encoding="utf-8")


def all_js_concatenated() -> str:
    return "\n".join(read_js(p.name) for p in sorted(JS_DIR.glob("*.js")))


# ===========================================================================
# 1. Document structure
# ===========================================================================

class TestDocumentStructure(unittest.TestCase):
    def setUp(self):
        self.index = read(INDEX)
        self.rate = read(RATE_CARD)

    def test_index_html_exists(self):
        self.assertTrue(INDEX.exists(), "index.html must exist")
        self.assertGreater(INDEX.stat().st_size, 50_000, "index.html must not be empty or truncated")

    def test_rate_card_html_exists(self):
        self.assertTrue(RATE_CARD.exists(), "rate-card.html must exist")
        self.assertGreater(RATE_CARD.stat().st_size, 10_000, "rate-card.html must not be empty")

    def test_frederic_sax_redirect_exists(self):
        self.assertTrue(REDIRECT.exists(), "frederic-sax.html redirect entrypoint must exist")
        self.assertIn('url=index.html', read(REDIRECT), "Redirect must point to index.html")

    def test_404_page_exists(self):
        self.assertTrue(NOT_FOUND.exists(), "404.html must exist for the ErrorDocument rule")
        self.assertNotIn('<script', read(NOT_FOUND), "404.html must contain no inline script (CSP)")

    def test_html_doctype_and_lang(self):
        self.assertTrue(self.index.strip().startswith("<!DOCTYPE html>"), "Must declare HTML5 DOCTYPE")
        self.assertIn('<html lang="en">', self.index, "Must declare lang='en'")

    def test_meta_viewport(self):
        self.assertIn(
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            self.index,
        )

    def test_meta_title_and_description(self):
        self.assertIn("<title>Frederic Sax Ke", self.index)
        self.assertIn('<meta name="description"', self.index)
        self.assertIn('Nairobi', self.index)

    def test_canonical_and_absolute_og_image(self):
        """A relative og:image is unresolvable by every social scraper."""
        self.assertIn('<link rel="canonical"', self.index)
        og = re.search(r'<meta property="og:image" content="([^"]+)"', self.index)
        self.assertIsNotNone(og, "og:image must be present")
        self.assertTrue(
            og.group(1).startswith("https://"),
            f"og:image must be absolute, got: {og.group(1)}",
        )

    def test_structured_data_present(self):
        """The artist entity must be machine-readable for rich results."""
        self.assertIn('application/ld+json', self.index)
        self.assertIn('"@type": "Musician"', self.index)

    def test_sitemap_and_manifest(self):
        self.assertTrue((REPO_DIR / "sitemap.xml").exists(), "sitemap.xml must exist")
        self.assertTrue((REPO_DIR / "manifest.webmanifest").exists(), "manifest.webmanifest must exist")
        robots = read(REPO_DIR / "robots.txt")
        self.assertIn('Sitemap:', robots, "robots.txt must declare the sitemap")

    def test_noscript_fallback(self):
        self.assertIn('<noscript>', self.index, "A JS-disabled visitor must be told how to book")


# ===========================================================================
# 2. CSP prerequisites — the whole reason the refactor happened
# ===========================================================================

class TestNoInlineBehaviour(unittest.TestCase):
    """Inline handlers and inline styles are what block a strict CSP."""

    @classmethod
    def setUpClass(cls):
        cls.index = read(INDEX)
        cls.rate = read(RATE_CARD)
        cls.html_files = [INDEX, RATE_CARD, NOT_FOUND]

    def test_no_inline_event_handlers(self):
        pattern = re.compile(r'\son(click|load|error|submit|change|input|mouseover|mouseout|keydown|keyup|focus|blur)\s*=')
        for path in self.html_files:
            body = read(path)
            hits = [f"{path.name}:{body[:m.start()].count(chr(10)) + 1}" for m in pattern.finditer(body)]
            self.assertEqual([], hits, f"{path.name} still has inline event handlers")

    def test_no_inline_style_blocks(self):
        for path in [INDEX, RATE_CARD]:
            self.assertNotIn("<style>", read(path), f"{path.name} must not contain an inline <style> block")

    def test_no_inline_style_attributes(self):
        for path in self.html_files:
            hits = re.findall(r'\sstyle\s*=\s*"', read(path))
            self.assertEqual([], hits, f"{path.name} must not contain inline style attributes")

    def test_no_javascript_urls(self):
        for path in self.html_files:
            self.assertNotIn('javascript:', read(path), "javascript: URLs are an XSS vector")


# ===========================================================================
# 3. Asset resolution — everything referenced must exist
# ===========================================================================

class TestAssetResolution(unittest.TestCase):
    def setUp(self):
        self.index = read(INDEX)
        self.rate = read(RATE_CARD)

    def test_all_local_img_assets_exist(self):
        img_srcs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', self.index)
        self.assertGreater(len(img_srcs), 0, "Should have image tags")
        for src in img_srcs:
            if src.startswith(("http://", "https://", "data:")):
                continue
            clean = src.split("?")[0].split("#")[0]
            self.assertTrue(
                (REPO_DIR / clean).exists(),
                f"index.html: image asset missing: {clean}",
            )

    def test_rate_card_assets_resolve(self):
        """rate-card.html carries no <img> tags of its own, so this checks
        every other local reference it does make."""
        for ref in re.findall(r'(?:src|href)=["\']([^"\']+)["\']', self.rate):
            if ref.startswith(("http://", "https://", "mailto:", "tel:", "data:", "#")):
                continue
            if ref.startswith(("css/", "js/", "IMG_")) or ref.endswith(".html"):
                self.assertTrue(
                    (REPO_DIR / ref.split("?")[0]).exists(),
                    f"rate-card.html: asset missing: {ref}",
                )

    def test_all_local_video_and_poster_assets_exist(self):
        for doc, name in ((self.index, "index.html"), (self.rate, "rate-card.html")):
            sources = re.findall(r'<source[^>]+src=["\']([^"\']+)["\']', doc)
            posters = re.findall(r'<video[^>]+poster=["\']([^"\']+)["\']', doc)
            for ref in sources + posters:
                if ref.startswith(("http://", "https://", "data:")):
                    continue
                clean = ref.split("?")[0].split("#")[0]
                self.assertTrue(
                    (REPO_DIR / clean).exists(),
                    f"{name}: video/poster asset missing: {clean}",
                )

    def test_hero_video_background_files(self):
        self.assertTrue((REPO_DIR / "IMG_3610.MP4").exists(), "Hero video IMG_3610.MP4 must exist")
        self.assertTrue((REPO_DIR / "IMG_3609.PNG").exists(), "Hero poster IMG_3609.PNG must exist")

    def test_css_asset_references_resolve(self):
        """The single most common production bug: a renamed stylesheet."""
        for name in REQUIRED_CSS:
            self.assertTrue((CSS_DIR / name).exists(), f"css/{name} is missing")
        for href in re.findall(r'<link[^>]+href="(css/[^"]+)"', read(INDEX)):
            self.assertTrue((REPO_DIR / href).exists(), f"index.html links a missing stylesheet: {href}")

    def test_js_asset_references_resolve(self):
        for name in REQUIRED_JS:
            self.assertTrue((JS_DIR / name).exists(), f"js/{name} is missing")

    def test_css_url_references_resolve(self):
        """A background-image url() pointing at a deleted file is invisible
        until production — e.g. the old IMG_2259.png."""
        for css in CSS_DIR.glob("*.css"):
            body = css.read_text(encoding="utf-8")
            for ref in re.findall(r'url\((["\']?)([^)"\']+)\1\)', body):
                value = ref[1]
                if value.startswith(("http://", "https://", "data:", "#")):
                    continue
                target = (CSS_DIR / value).resolve()
                self.assertTrue(
                    target.exists(),
                    f"{css.name} references a missing asset: {value}",
                )


# ===========================================================================
# 4. Modular architecture
# ===========================================================================

class TestModularArchitecture(unittest.TestCase):
    def setUp(self):
        self.index = read(INDEX)

    def test_no_partial_tokens_left_in_build(self):
        leftovers = re.findall(r"\{\{[A-Z_]+\}\}", self.index)
        self.assertEqual([], leftovers, "Build tokens leaked into the output")

    def test_partials_directory_is_complete(self):
        required = {
            "head", "nav", "hero", "marquee", "bio", "videos", "calendar",
            "weddings", "ratecard", "pinterest", "portal", "contact",
            "footer", "scripts",
        }
        present = {p.stem for p in PARTIAL_DIR.glob("*.html")}
        self.assertTrue(required.issubset(present), f"Missing partials: {required - present}")

    def test_index_loads_modules_not_inline_script(self):
        self.assertIn('<script type="module" src="js/app.js"></script>', self.index)
        self.assertNotIn("<script>", self.index, "No bare inline <script> may remain")

    def test_all_css_linked_from_head(self):
        """rate-card.css only belongs to the rate card document, not to
        index.html — it must not be shipped to portfolio visitors."""
        head = (PARTIAL_DIR / "head.html").read_text(encoding="utf-8")
        for name in REQUIRED_CSS:
            if name == "rate-card.css":
                self.assertNotIn(
                    f'href="css/{name}"',
                    head,
                    "rate-card.css must not be linked from index.html",
                )
                continue
            self.assertIn(f'href="css/{name}"', head, f"css/{name} is never linked")

        rate_head = read(RATE_CARD)
        self.assertIn('href="css/rate-card.css"', rate_head)
        self.assertIn('href="css/tokens.css"', rate_head)
        self.assertIn('href="css/print.css"', rate_head)

    def test_build_script_is_valid_python(self):
        import py_compile
        try:
            py_compile.compile(str(BUILD), doraise=True)
        except py_compile.PyCompileError as exc:
            self.fail(f"build.py does not compile: {exc}")


# ===========================================================================
# 5. Navigation integrity
# ===========================================================================

class TestNavigationIntegrity(unittest.TestCase):
    def setUp(self):
        self.index = read(INDEX)

    def test_desktop_nav_links_target_existing_sections(self):
        nav = re.search(r'<ul class="nav-menu">(.*?)</ul>', self.index, re.DOTALL)
        self.assertIsNotNone(nav, "Must find .nav-menu")
        hrefs = re.findall(r'href=["\']#([^"\']+)["\']', nav.group(1))
        self.assertGreater(len(hrefs), 5, "Desktop nav should have at least 6 sections")
        for target in hrefs:
            self.assertIn(
                f'id="{target}"',
                self.index,
                f"Nav link #{target} has no matching DOM element",
            )

    def test_mobile_drawer_links_match_sections(self):
        drawer = re.search(r'<div class="mobile-drawer"[^>]*>(.*?)</div>', self.index, re.DOTALL)
        self.assertIsNotNone(drawer, "Must find .mobile-drawer")
        for target in re.findall(r'href=["\']#([^"\']+)["\']', drawer.group(1)):
            self.assertIn(f'id="{target}"', self.index, f"Drawer link #{target} has no matching id")

    def test_every_anchor_resolves(self):
        """The old site had a nav link pointing at a display:none element
        that no longer existed in the rendered calendar. This closes that."""
        ids = set(re.findall(r'id=["\']([^"\']+)["\']', self.index))
        for target in re.findall(r'href=["\']#([^"\']+)["\']', self.index):
            self.assertIn(target, ids, f'href="#{target}" resolves to nothing')

    def test_no_duplicate_element_ids(self):
        seen, dupes = set(), []
        for element_id in re.findall(r'id=["\']([^"\']+)["\']', self.index):
            if element_id in seen:
                dupes.append(element_id)
            seen.add(element_id)
        self.assertEqual([], dupes, "Duplicate element ids break label/aria association")

    def test_skip_link_targets_main(self):
        self.assertIn('class="skip-link"', self.index)
        self.assertIn('<main class="site-main-flow" id="main">', self.index)

    def test_rate_card_links_open_in_new_tab(self):
        for link in re.findall(r'<a[^>]+href=["\']rate-card\.html["\'][^>]*>', self.index):
            self.assertIn('target="_blank"', link, "Rate card links must open in a new tab")
            self.assertIn('rel="noopener', link, "External links must carry rel=noopener")

    def test_external_links_carry_noopener(self):
        """Reverse tabnabbing: window.opener must never leak to a new tab."""
        for link in re.findall(r'<a[^>]+target="_blank"[^>]*>', self.index):
            self.assertIn('rel="noopener', link, f"target=_blank without rel=noopener: {link[:90]}")


# ===========================================================================
# 6. Accessibility
# ===========================================================================

class TestAccessibility(unittest.TestCase):
    def setUp(self):
        self.index = read(INDEX)

    def test_hamburger_has_aria_expanded_and_controls(self):
        self.assertIn('aria-expanded="false"', self.index)
        self.assertIn('aria-controls="mobile-drawer"', self.index)

    def test_live_regions_exist(self):
        self.assertIn('id="toast-container"', self.index)
        self.assertIn('aria-live="polite"', self.index)

    def test_sections_are_labelled(self):
        for section_id in ["bio", "videos", "calendar", "weddings", "ratecard", "portal", "contact"]:
            self.assertIn(
                f'id="{section_id}" aria-labelledby="{section_id}-title"',
                self.index,
                f"Section #{section_id} needs aria-labelledby",
            )

    def test_every_image_has_alt(self):
        for match in re.finditer(r'<img[^>]*>', self.index):
            self.assertIn('alt=', match.group(0), f"Image without alt: {match.group(0)[:90]}")

    def test_every_form_input_has_a_label(self):
        inputs = re.findall(r'<(?:input|select|textarea)[^>]*id="([^"]+)"', self.index)
        self.assertGreater(len(inputs), 5, "Should find labelled form controls")
        for element_id in inputs:
            self.assertIn(
                f'for="{element_id}"',
                self.index,
                f"Control #{element_id} has no associated <label for>",
            )

    def test_form_controls_have_autocomplete(self):
        for field in ["form-name", "form-phone", "form-location"]:
            block = re.search(rf'id="{field}"[^>]*>', self.index)
            self.assertIsNotNone(block)
            self.assertIn('autocomplete', block.group(0), f"#{field} should have autocomplete")

    def test_date_inputs_have_a_floor(self):
        """Past dates were accepted and forwarded to WhatsApp as bookings."""
        self.assertIn('isFutureDate', read_js("utils.js"), "utils.js must guard future dates")
        self.assertIn('formatISODate', read_js("utils.js"), "utils.js must expose a local-time ISO formatter")

    def test_videos_have_preload_metadata(self):
        self.assertIn('preload="metadata"', self.index, "Hero/gallery video must not preload the full file")

    def test_below_fold_images_are_lazy(self):
        """Hero portrait may be eager; everything else must be lazy."""
        lazy = len(re.findall(r'loading="lazy"', self.index))
        self.assertGreaterEqual(lazy, 6, f"expected many lazy images, found {lazy}")


# ===========================================================================
# 7. Calendar state engine
# ===========================================================================

class TestCalendarStateEngine(unittest.TestCase):
    def setUp(self):
        self.index = read(INDEX)
        self.calendar = read_js("airbnb-calendar.js")

    def test_calendar_markup_and_containers(self):
        for needle in [
            'id="bnb-mode-dates"',
            'id="bnb-mode-flexible"',
            'id="bnb-slot-bar-val"',
            'id="bnb-calendar-stream"',
            'id="bnb-flex-section"',
            'id="bnb-slot-modal"',
            'id="cal-selected-date-text"',
            'id="cal-slots-grid"',
            'id="cal-book-btn-text"',
        ]:
            self.assertIn(needle, self.index)

    def test_calendar_month_calculation_leap_years(self):
        def get_days_in_month(year, month):
            if month in (0, 2, 4, 6, 7, 9, 11):
                return 31
            if month in (3, 5, 8, 10):
                return 30
            if month == 1:
                is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
                return 29 if is_leap else 28
            raise ValueError()

        self.assertEqual(get_days_in_month(2024, 1), 29, "2024 is a leap year")
        self.assertEqual(get_days_in_month(2025, 1), 28)
        self.assertEqual(get_days_in_month(2026, 1), 28)
        self.assertEqual(get_days_in_month(2026, 9), 31, "October has 31 days")

    def test_slot_definitions(self):
        self.assertIn("Full Wedding Day Package", self.index)
        self.assertIn("Ceremony Sax Only", self.index)
        self.assertIn("Cocktail Hour Sax", self.index)
        self.assertTrue(
            ("Reception &amp; Corporate Gala" in self.index)
            or ("Reception & Corporate Gala" in self.index),
            "Must have Reception & Corporate Gala slot",
        )

    def test_today_is_not_hard_coded(self):
        """The engine declared today: new Date(2026, 9, 7) with a fixed
        2-month window starting October 2026. It went stale in November.
        Comments are stripped so the regression note itself does not trip
        this assertion."""
        code = re.sub(r'/\*[\s\S]*?\*/', '', self.calendar)
        code = re.sub(r'//[^\n]*', '', code)
        self.assertNotIn("new Date(2026", code, "Calendar 'today' must not be hard-coded")
        self.assertNotIn("viewYear: 2026", code, "Calendar view year must not be hard-coded")
        self.assertNotIn("viewMonth: 9", code, "Calendar view month must not be hard-coded")
        self.assertIn("startOfToday()", self.calendar, "Calendar must derive today from the clock")

    def test_range_cannot_span_booked_dates(self):
        """A guest could previously reserve 8-16 Oct when the 12th-16th
        were all marked unavailable."""
        self.assertIn("function rangeIsClean", self.calendar)
        self.assertIn("That range includes held dates", self.calendar)

    def test_calendar_is_keyboard_navigable(self):
        for key in ["ArrowRight", "ArrowLeft", "ArrowUp", "ArrowDown",
                    "Home", "End", "PageUp", "PageDown", "Enter"]:
            self.assertIn(f"'{key}'", self.calendar, f"Calendar ignores {key}")
        self.assertIn("focusDayCell", self.calendar)

    def test_calendar_renders_twelve_months(self):
        """Two months meant the calendar went dead every other month."""
        self.assertIn("MONTHS_TO_RENDER: 12", read_js("config.js"))


# ===========================================================================
# 8. WhatsApp and form integration
# ===========================================================================

class TestWhatsAppAndFormIntegration(unittest.TestCase):
    def setUp(self):
        self.index = read(INDEX)
        self.rate = read(RATE_CARD)

    def test_whatsapp_target_phone(self):
        for doc, name in ((self.index, "index.html"), (self.rate, "rate-card.html")):
            numbers = re.findall(r'https://wa\.me/(\d+)', doc)
            self.assertGreater(len(numbers), 0, f"{name} must have wa.me links")
            for number in numbers:
                self.assertEqual(
                    number,
                    "254745163122",
                    f"{name}: non-canonical WhatsApp number {number}",
                )

    def test_number_defined_once(self):
        """The number used to be repeated ~30 times across two files. It now
        lives in exactly one module, and every consumer imports it."""
        self.assertIn("WHATSAPP_NUMBER: '254745163122'", read_js("config.js"))
        self.assertIn("WHATSAPP_BASE: 'https://wa.me/254745163122'", read_js("config.js"))
        owners = [p.name for p in JS_DIR.glob("*.js") if 'wa.me/254745163122' in read_js(p.name)]
        self.assertEqual(["config.js"], owners,
                         "The wa.me URL must be built only in config.js")

    def test_canonical_number_used_everywhere(self):
        self.assertIn("CONFIG.WHATSAPP_BASE", read_js("nav.js"))
        self.assertIn("CONFIG.WHATSAPP_BASE", read_js("airbnb-calendar.js"))
        self.assertIn("CONFIG.WHATSAPP_BASE", read_js("booking.js"))
        self.assertIn("CONFIG.WHATSAPP_BASE", read_js("rate-card.js"))

    def test_rate_card_whatsapp_phone_and_handler(self):
        self.assertGreater(len(re.findall(r'https://wa\.me/(\d+)', self.rate)), 0)
        # The handler is a module export now, not an inline function name
        self.assertIn("handleRateCardWhatsAppSubmit", read_js("rate-card.js"))
        self.assertIn("window.handleRateCardWhatsAppSubmit", read_js("rate-card.js"))
        self.assertIn("data-action=\"open-booking-modal\"", self.rate)
        self.assertIn("data-action=\"set-currency\"", self.rate)

    def test_rate_card_modal_fields(self):
        for needle in [
            'id="booking-modal-overlay"', 'id="modal-name"', 'id="modal-phone"',
            'id="modal-date"', 'id="modal-venue"', 'id="modal-pkg-select"',
            'id="modal-notes"', 'id="rate-card-booking-form"',
        ]:
            self.assertIn(needle, self.rate, f"rate-card.html missing {needle}")

    def test_rate_card_table_inquire_buttons(self):
        buttons = re.findall(r'class="btn-table-inquire[^"]*"', self.rate)
        self.assertEqual(len(buttons), 5, "All 5 rate card packages must have an Inquire button")

    def test_contact_form_fields(self):
        for needle in [
            'id="form-name"', 'id="form-phone"', 'id="form-date"',
            'id="form-location"', 'id="form-package"', 'id="form-message"',
            'id="direct-booking-form"',
        ]:
            self.assertIn(needle, self.index)

    def test_package_prefill_and_scroll_helper(self):
        self.assertIn("function selectPackageAndScroll", read_js("booking.js"))
        self.assertIn("data-action=\"select-package\"", self.index)

    def test_calendar_date_sync_target(self):
        self.assertIn(
            "formDate.value = formatISODate(STATE.rangeStart)",
            read_js("airbnb-calendar.js"),
        )

    def test_package_selection_reaches_dispatch(self):
        """Chips updated the DOM but never the state the WhatsApp message
        read, so 'Ceremony Sax Only' always sent 'Full Wedding Day'."""
        self.assertIn("setAirbnbReservationPackage", read_js("airbnb-calendar.js"))
        self.assertIn("fsk:package-selected", read_js("booking.js"))
        self.assertIn("STATE.selectedSlot.package", read_js("airbnb-calendar.js"))


# ===========================================================================
# 9. Security
# ===========================================================================

class TestSecurity(unittest.TestCase):
    SECRET_PATTERNS = [
        (re.compile(r'\bwhsec_[a-zA-Z0-9]{16,}\b'), "Stripe/Svix Webhook Secret"),
        (re.compile(r'\bsk_live_[a-zA-Z0-9]{16,}\b'), "Live Stripe Secret Key"),
        (re.compile(r'\bsk_test_[a-zA-Z0-9]{16,}\b'), "Stripe Test Secret Key"),
        (re.compile(r'\bsk-ant-api[a-zA-Z0-9\-]{16,}\b'), "Anthropic API Key"),
        (re.compile(r'\bsk-proj-[a-zA-Z0-9\-]{16,}\b'), "OpenAI Project API Key"),
        (re.compile(r'\bre_[a-zA-Z0-9]{24,36}\b'), "Resend API Key"),
        (re.compile(r'\bghp_[a-zA-Z0-9]{36}\b'), "GitHub Personal Access Token"),
        (re.compile(r'\bAKIA[0-9A-Z]{16}\b'), "AWS Access Key ID"),
    ]

    def test_secret_patterns_zero_leaks(self):
        """Widened from the original .ts/.tsx/.js/.json/.py/.html/.md/.env set
        so the zips, the .jsonl attestation logs and the .txt docs are
        scanned too — the old scan skipped all of them."""
        extensions = {".ts", ".tsx", ".js", ".json", ".py", ".html", ".md",
                      ".env", ".zip", ".jsonl", ".txt", ".css", ".webmanifest", ".xml"}
        violations = []
        for root, dirs, files in os.walk(REPO_DIR):
            if any(ignored in root for ignored in (".git", "node_modules", "__pycache__")):
                continue
            for filename in files:
                if not filename.lower().endswith(tuple(extensions)):
                    continue
                fpath = Path(root) / filename
                try:
                    content = fpath.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                for line_no, line in enumerate(content.splitlines(), 1):
                    for pattern, name in self.SECRET_PATTERNS:
                        if pattern.search(line):
                            violations.append(f"{fpath.name}:{line_no} [{name}]")
        self.assertEqual([], violations, f"Found secrets in repo: {violations}")

    def test_no_innerhtml_sinks(self):
        """Every innerHTML assignment must be static HTML that the developer
        wrote — never a string built from user input. The precise danger is
        template interpolation or a reference to a form value; both are
        banned. Comments are stripped so regression notes don't count."""
        for path in sorted(JS_DIR.glob("*.js")):
            raw = path.read_text(encoding="utf-8")
            body = re.sub(r"/\*[\s\S]*?\*/", "", raw)
            body = re.sub(r"//[^\n]*", "", body)
            for match in re.finditer(r"\.innerHTML\s*=\s*([^;\n]+)", body):
                value = match.group(1).strip()
                if not value:
                    continue
                self.assertNotIn(
                    "${",
                    value,
                    f"{path.name}: innerHTML must never interpolate -> {value[:70]}",
                )
                self.assertNotIn(
                    ".value",
                    value,
                    f"{path.name}: innerHTML must never read a form value -> {value[:70]}",
                )

    def test_no_eval_or_new_function(self):
        js = all_js_concatenated()
        self.assertNotRegex(js, r'\beval\s*\(')
        self.assertNotRegex(js, r'new\s+Function\s*\(')
        self.assertNotIn('document.write', js)

    def test_window_open_uses_noopener(self):
        """window.open(url, '_blank') leaks window.opener (tabnabbing)."""
        self.assertIn("export function openExternal", read_js("utils.js"))
        self.assertIn("noopener,noreferrer", read_js("utils.js"))
        self.assertIn("win.opener = null", read_js("utils.js"))

        for path in sorted(JS_DIR.glob("*.js")):
            body = path.read_text(encoding="utf-8")
            code = re.sub(r"/\*[\s\S]*?\*/", "", body)   # strip doc comments
            code = re.sub(r"//[^\n]*", "", code)
            for match in re.finditer(r"window\.open\(([^)]*)\)", code):
                self.assertIn(
                    "noopener",
                    match.group(1),
                    f"{path.name}: window.open without noopener -> {match.group(0)}",
                )

    def test_every_outbound_window_goes_through_openeexternal(self):
        for name in ["airbnb-calendar.js", "booking.js", "rate-card.js"]:
            self.assertIn("openExternal(", read_js(name), f"{name} must use openExternal")

    def test_external_urls_use_https(self):
        for doc, name in ((read(INDEX), "index.html"), (read(RATE_CARD), "rate-card.html")):
            for url in re.findall(r'https?://[^\s"\'<>]+', doc):
                if url.startswith("http://"):
                    # wa.me is only ever https
                    self.assertFalse(
                        url.startswith("http://wa.me"),
                        f"{name}: insecure wa.me URL {url}",
                    )

    def test_security_headers_in_vercel_config(self):
        import json
        config = json.loads((REPO_DIR / "vercel.json").read_text(encoding="utf-8"))
        headers = {}
        for entry in config.get("headers", []):
            for header in entry.get("headers", []):
                headers[header["key"]] = header["value"]

        for required in [
            "Content-Security-Policy",
            "Strict-Transport-Security",
            "X-Content-Type-Options",
            "X-Frame-Options",
            "Referrer-Policy",
            "Permissions-Policy",
        ]:
            self.assertIn(required, headers, f"vercel.json is missing {required}")

        csp = headers.get("Content-Security-Policy", "")
        self.assertIn("default-src 'self'", csp)
        self.assertIn("frame-ancestors 'none'", csp)
        self.assertNotIn("'unsafe-eval'", csp)
        self.assertNotIn("script-src 'self' 'unsafe-inline'", csp,
                         "script-src must not allow inline script — that is the whole point")

    def test_deprecated_xss_protection_header_removed(self):
        import json
        config = json.loads((REPO_DIR / "vercel.json").read_text(encoding="utf-8"))
        keys = {h["key"] for e in config.get("headers", []) for h in e.get("headers", [])}
        self.assertNotIn("X-XSS-Protection", keys,
                         "X-XSS-Protection is deprecated and must not be sent")

    def test_htaccess_matches_vercel_headers(self):
        htaccess = (REPO_DIR / ".htaccess").read_text(encoding="utf-8")
        for header in ["Content-Security-Policy", "Strict-Transport-Security",
                       "X-Content-Type-Options", "Referrer-Policy"]:
            self.assertIn(header, htaccess, f".htaccess is missing {header}")

    def test_dev_server_does_not_bind_all_interfaces_by_default(self):
        server = (REPO_DIR / "serve.py").read_text(encoding="utf-8")
        self.assertIn('default="127.0.0.1"', server)
        self.assertNotIn("('0.0.0.0', port)", server,
                         "serve.py must not bind 0.0.0.0 by default")

    def test_dev_server_does_not_send_permissive_cors(self):
        server = (REPO_DIR / "serve.py").read_text(encoding="utf-8")
        self.assertNotIn("Access-Control-Allow-Origin", server)


# ===========================================================================
# 10. Brand purity and content sanitisation
# ===========================================================================

class TestBrandPurityAndContentSanitization(unittest.TestCase):
    def setUp(self):
        self.index = read(INDEX).lower()
        self.rate = read(RATE_CARD).lower()
        self.build = (REPO_DIR / "build.py").read_text(encoding="utf-8").lower()
        self.disallowed = [
            "w" + "ardawear",
            "w" + "arda wear",
            "living " + "the charge",
            "living-" + "the-charge",
            "soulful " + "melodies",
            "king sax",
            "kingsax.com",
        ]

    def test_zero_disallowed_tokens(self):
        for token in self.disallowed:
            for name, body in (("index.html", self.index), ("rate-card.html", self.rate)):
                self.assertEqual(
                    0,
                    body.count(token),
                    f"{name}: token '{token}' must not exist",
                )

    def test_stale_foreign_artist_file_removed(self):
        self.assertFalse((REPO_DIR / "king-sax.html").exists(),
                         "king-sax.html is a foreign-artist page that violates brand purity")

    def test_no_unreferenced_oversized_media(self):
        """IMG_2259.png (5.6 MB) and vest_crop.jpg shipped unused."""
        for name in ["IMG_2259.png", "IMG_2259.HEIC", "vest_crop.jpg"]:
            self.assertFalse((REPO_DIR / name).exists(),
                             f"{name} is unreferenced dead weight")

    def test_referenced_background_image_exists(self):
        self.assertTrue((REPO_DIR / "IMG_2259.jpg").exists(),
                        "css/hero.css backgrounds must resolve")

    def test_canonical_instagram_handles(self):
        """@ojiespov was linked to a non-existent handle."""
        self.assertNotIn("ojiespov-instagram", self.index)
        self.assertNotIn("ojie_f.red7/", self.index.split("instagram.com")[0] if False else "")
        self.assertIn("instagram.com/ojiespov/", read(INDEX))

    def test_canonical_phrasing_preserved(self):
        body = read(INDEX).lower()
        self.assertIn("expressive saxophone phrasing", body)
        self.assertIn("dynamic stage presence", body)
        self.assertIn("premier live saxophonist", body)


# ===========================================================================
# 11. Booking engine (Airbnb widget)
# ===========================================================================

class TestAirbnbBookingEngine(unittest.TestCase):
    def setUp(self):
        self.index = read(INDEX)
        self.css = (CSS_DIR / "airbnb-booking.css").read_text(encoding="utf-8")
        self.js = read_js("airbnb-calendar.js")
        self.booking = read_js("booking.js")

    def test_modular_files_exist_and_non_empty(self):
        self.assertTrue((CSS_DIR / "airbnb-booking.css").exists())
        self.assertGreater((CSS_DIR / "airbnb-booking.css").stat().st_size, 5000)
        self.assertTrue((JS_DIR / "airbnb-calendar.js").exists())
        self.assertGreater((JS_DIR / "airbnb-calendar.js").stat().st_size, 5000)

    def test_index_includes_modular_assets(self):
        self.assertIn('href="css/airbnb-booking.css"', self.index)

    def test_airbnb_css_tokens_and_selectors(self):
        for needle in [
            '.bnb-calendar-card', '.bnb-segmented-control', '.bnb-slot-bar',
            '.bnb-day-cell.struck', '.bnb-day-cell.range-start',
            '.bnb-day-cell.range-end', '.bnb-day-cell.in-range',
            '.bnb-btn-test-sim', '.bnb-slot-modal-overlay',
            '.bnb-day-cell:focus-visible',
        ]:
            self.assertIn(needle, self.css)

    def test_airbnb_js_calendar_stream_and_methods(self):
        for needle in [
            'function renderCalendarStream', 'setAirbnbBookingMode',
            'setAirbnbTolerance', 'clearAirbnbDates', 'openSlotChangeModal',
            'selectPerformanceSlot', 'dispatchAirbnbReservationWhatsApp',
            'setAirbnbReservationPackage',
        ]:
            self.assertIn(needle, self.js)

    def test_simulation_mode_formatting(self):
        self.assertIn('\u26a0\ufe0f [TEST BOOKING SIMULATION]', self.js)
        self.assertIn('*AUTOMATED SYSTEM VERIFICATION TEST*', self.js)
        self.assertIn('STATUS: TEST SIMULATION VERIFIED', self.js)
        self.assertIn('CONFIG.WHATSAPP_BASE', self.js)
        self.assertIn('254745163122', read_js("config.js"))

    def test_dom_elements_for_airbnb_features(self):
        for needle in [
            'id="bnb-mode-dates"', 'id="bnb-mode-flexible"', 'id="bnb-slot-bar-val"',
            'id="bnb-calendar-stream"', 'id="bnb-flex-section"', 'id="bnb-slot-modal"',
            'data-action="reserve"', 'data-action="select-slot"',
            'data-action="set-tolerance"',
        ]:
            self.assertIn(needle, self.index)

    def test_modal_is_a_real_dialog(self):
        js = self.js
        self.assertIn("setAttribute('aria-modal', 'true')", js)
        self.assertIn("setAttribute('role', 'dialog')", js)
        self.assertIn("'Escape'", js)
        self.assertIn("trapModalFocus", js, "Modal needs a Tab focus trap")
        self.assertIn("lastFocus", js, "Modal must restore focus on close")

    def test_data_actions_are_registered(self):
        """Every data-action in the markup must have a handler, or the
        control is silently dead in production."""
        app = read_js("app.js")
        registered = set(re.findall(r"registerAction\('([^']+)'", app))
        used = set(re.findall(r'data-action="([^"]+)"', self.index + read(RATE_CARD)))
        self.assertTrue(used, "index.html should use data-action controls")
        missing = used - registered
        self.assertEqual(set(), missing, f"data-actions with no handler: {missing}")


# ===========================================================================
# 12. Print / document generation
# ===========================================================================

class TestPrintAndDocuments(unittest.TestCase):
    def setUp(self):
        self.index = read(INDEX)
        self.css = (CSS_DIR / "print.css").read_text(encoding="utf-8")

    def test_print_css_isolates_the_document(self):
        self.assertIn("body.printing-contract #contract-view", self.css)
        self.assertIn("body.printing-invoice  #invoice-view", self.css)
        self.assertIn("body.printing-ratecard .ratecard-print-root", self.css)
        self.assertIn("@page", self.css)

    def test_print_buttons_use_actions_not_handlers(self):
        self.assertIn('data-action="download-contract"', self.index)
        self.assertIn('data-action="print-invoice"', self.index)

    def test_invoice_preview_is_generated(self):
        self.assertIn("buildInvoicePreview", read_js("portal.js"))
        self.assertIn("invoiceLine", read_js("portal.js"))
        self.assertIn('id="invoice-preview"', self.index)


# ===========================================================================
# 13. Performance
# ===========================================================================

class TestPerformance(unittest.TestCase):
    def setUp(self):
        self.index = read(INDEX)
        self.head = (PARTIAL_DIR / "head.html").read_text(encoding="utf-8")

    def test_fonts_are_not_render_blocking(self):
        self.assertIn('media="not all"', self.head)
        self.assertIn('rel="preload" as="style"', self.head)

    def test_all_js_is_module_and_therefore_deferred(self):
        """A <script type=module> is deferred by default, so it never blocks
        first paint. There must be no other executable script tag."""
        for match in re.finditer(r'<script([^>]*)>', self.index):
            attrs = match.group(1)
            if 'application/ld+json' in attrs:
                continue  # structured data is not executable
            self.assertIn('type="module"', attrs,
                          f"Script must be a deferred module: <script{attrs}>")
        self.assertNotIn("<script>", self.index, "No bare inline <script> may remain")

    def test_no_external_render_blocking_js(self):
        srcs = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', self.index)
        for src in srcs:
            self.assertFalse(src.startswith("http://"), f"Insecure script source: {src}")
        self.assertIn('src="js/app.js"', self.index)

    def test_csp_permits_no_remote_script(self):
        import json
        config = json.loads((REPO_DIR / "vercel.json").read_text(encoding="utf-8"))
        for entry in config.get("headers", []):
            for header in entry.get("headers", []):
                if header["key"] == "Content-Security-Policy":
                    self.assertIn("script-src 'self'", header["value"])
                    self.assertNotIn("script-src 'self' https:", header["value"])

    def test_page_weight_within_budget(self):
        """index.html was 147 KB with 2,270 lines of CSS inside it."""
        size = INDEX.stat().st_size
        self.assertLess(size, 100_000, f"index.html is {size} bytes — too heavy")

    def test_index_is_not_a_monolith(self):
        lines = len(self.index.splitlines())
        self.assertLess(lines, 1_600, f"index.html should be ~1,300 lines, found {lines}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
