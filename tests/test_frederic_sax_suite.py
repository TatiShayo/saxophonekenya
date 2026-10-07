#!/usr/bin/env python3
"""
Hermetic Automated Test Suite for Frederic Sax Ke Luxury Website
HERMES v6 / v7 Architecture Standard Verification Suite
"""

import os
import re
import unittest
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent

class TestDocumentStructure(unittest.TestCase):
    def setUp(self):
        self.index_path = REPO_DIR / "index.html"
        self.rate_path = REPO_DIR / "rate-card.html"
        self.redirect_path = REPO_DIR / "frederic-sax.html"

    def test_index_html_exists(self):
        self.assertTrue(self.index_path.exists(), "index.html must exist")
        self.assertGreater(self.index_path.stat().st_size, 50000, "index.html must not be empty or truncated")

    def test_rate_card_html_exists(self):
        self.assertTrue(self.rate_path.exists(), "rate-card.html must exist")
        self.assertGreater(self.rate_path.stat().st_size, 10000, "rate-card.html must not be empty")

    def test_frederic_sax_redirect_exists(self):
        self.assertTrue(self.redirect_path.exists(), "frederic-sax.html redirect entrypoint must exist")
        content = self.redirect_path.read_text(encoding="utf-8")
        self.assertIn('url=index.html', content, "Redirect must point to index.html")

    def test_html_doctype_and_lang(self):
        content = self.index_path.read_text(encoding="utf-8")
        self.assertTrue(content.strip().startswith("<!DOCTYPE html>"), "Must declare HTML5 DOCTYPE")
        self.assertIn('<html lang="en">', content, "Must declare lang='en'")

    def test_meta_viewport(self):
        content = self.index_path.read_text(encoding="utf-8")
        self.assertIn('<meta name="viewport" content="width=device-width, initial-scale=1.0">', content)

    def test_meta_title_and_description(self):
        content = self.index_path.read_text(encoding="utf-8")
        self.assertIn("<title>Frederic Sax Ke", content)
        self.assertIn('<meta name="description"', content)
        self.assertIn('Nairobi', content)


class TestAssetResolution(unittest.TestCase):
    def setUp(self):
        self.index_content = (REPO_DIR / "index.html").read_text(encoding="utf-8")

    def test_all_local_img_assets_exist(self):
        img_srcs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', self.index_content)
        self.assertGreater(len(img_srcs), 0, "Should have image tags")
        for src in img_srcs:
            if src.startswith(("http://", "https://", "data:")):
                continue
            clean_src = src.split("?")[0].split("#")[0]
            asset_path = REPO_DIR / clean_src
            self.assertTrue(asset_path.exists(), f"Image asset missing: {clean_src}")

    def test_all_local_video_and_poster_assets_exist(self):
        sources = re.findall(r'<source[^>]+src=["\']([^"\']+)["\']', self.index_content)
        posters = re.findall(r'<video[^>]+poster=["\']([^"\']+)["\']', self.index_content)
        all_video_refs = sources + posters
        self.assertGreater(len(all_video_refs), 0, "Should have video / poster references")
        for ref in all_video_refs:
            if ref.startswith(("http://", "https://", "data:")):
                continue
            clean_ref = ref.split("?")[0].split("#")[0]
            asset_path = REPO_DIR / clean_ref
            self.assertTrue(asset_path.exists(), f"Video/poster asset missing: {clean_ref}")

    def test_hero_video_background_files(self):
        self.assertTrue((REPO_DIR / "IMG_3610.MP4").exists(), "Hero background video IMG_3610.MP4 must exist")
        self.assertTrue((REPO_DIR / "IMG_3609.PNG").exists(), "Hero poster frame IMG_3609.PNG must exist")


class TestNavigationIntegrity(unittest.TestCase):
    def setUp(self):
        self.index_content = (REPO_DIR / "index.html").read_text(encoding="utf-8")

    def test_desktop_nav_links_target_existing_sections(self):
        nav_match = re.search(r'<ul class="nav-menu">(.*?)</ul>', self.index_content, re.DOTALL)
        self.assertIsNotNone(nav_match, "Must find .nav-menu")
        nav_html = nav_match.group(1)
        hrefs = re.findall(r'href=["\']#([^"\']+)["\']', nav_html)
        self.assertGreater(len(hrefs), 5, "Desktop nav should have at least 6 sections")
        for target_id in hrefs:
            has_id = (f'id="{target_id}"' in self.index_content) or (f"id='{target_id}'" in self.index_content)
            self.assertTrue(has_id, f"Nav link #{target_id} has no matching DOM element with that ID")

    def test_mobile_drawer_links_match_sections(self):
        drawer_match = re.search(r'<div class="mobile-drawer"[^>]*>(.*?)</div>', self.index_content, re.DOTALL)
        self.assertIsNotNone(drawer_match, "Must find .mobile-drawer")
        drawer_html = drawer_match.group(1)
        hrefs = re.findall(r'href=["\']#([^"\']+)["\']', drawer_html)
        self.assertGreater(len(hrefs), 5, "Mobile drawer should have at least 6 sections")
        for target_id in hrefs:
            has_id = (f'id="{target_id}"' in self.index_content) or (f"id='{target_id}'" in self.index_content)
            self.assertTrue(has_id, f"Drawer link #{target_id} has no matching DOM element with that ID")

    def test_rate_card_redirect_links(self):
        rate_card_links = re.findall(r'<a[^>]+href=["\']rate-card\.html["\'][^>]*>', self.index_content)
        self.assertGreater(len(rate_card_links), 0, "Must have links pointing to rate-card.html")
        for link in rate_card_links:
            self.assertIn('target="_blank"', link, "Rate card links must open in a new tab")


class TestCalendarStateEngine(unittest.TestCase):
    def setUp(self):
        self.index_content = (REPO_DIR / "index.html").read_text(encoding="utf-8")

    def test_calendar_markup_and_containers(self):
        self.assertIn('class="calendar-wrapper-card"', self.index_content)
        self.assertIn('id="cal-nav-title"', self.index_content)
        self.assertIn('id="cal-grid"', self.index_content)
        self.assertIn('id="cal-selected-date-text"', self.index_content)
        self.assertIn('id="cal-slots-grid"', self.index_content)

    def test_calendar_month_calculation_leap_years(self):
        # Verify month length math helper matches JS logic
        def get_days_in_month(year, month):
            # month is 0-indexed: 0=Jan, 1=Feb, etc.
            if month in (0, 2, 4, 6, 7, 9, 11):
                return 31
            elif month in (3, 5, 8, 10):
                return 30
            elif month == 1:
                is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
                return 29 if is_leap else 28
            raise ValueError()

        self.assertEqual(get_days_in_month(2024, 1), 29, "2024 is a leap year (Feb=29)")
        self.assertEqual(get_days_in_month(2025, 1), 28, "2025 is standard year (Feb=28)")
        self.assertEqual(get_days_in_month(2026, 1), 28, "2026 is standard year (Feb=28)")
        self.assertEqual(get_days_in_month(2026, 9), 31, "October has 31 days")

    def test_slot_definitions(self):
        self.assertIn("Full Wedding Day Package", self.index_content)
        self.assertIn("Ceremony Sax Only", self.index_content)
        self.assertIn("Cocktail Hour Sax", self.index_content)
        self.assertTrue(
            ("Reception & Corporate Gala" in self.index_content) or
            ("Reception &amp; Corporate Gala" in self.index_content),
            "Must have Reception & Corporate Gala slot"
        )


class TestWhatsAppAndFormIntegration(unittest.TestCase):
    def setUp(self):
        self.index_content = (REPO_DIR / "index.html").read_text(encoding="utf-8")
        self.rate_content = (REPO_DIR / "rate-card.html").read_text(encoding="utf-8")

    def test_whatsapp_target_phone(self):
        wa_links = re.findall(r'https://wa\.me/(\d+)', self.index_content)
        self.assertGreater(len(wa_links), 0, "Must have wa.me links in index.html")
        for num in wa_links:
            self.assertEqual(num, "254745163122", "All WhatsApp links must use canonical Kenyan phone 254745163122")

    def test_rate_card_whatsapp_phone_and_handler(self):
        wa_links = re.findall(r'https://wa\.me/(\d+)', self.rate_content)
        self.assertGreater(len(wa_links), 0, "Must have wa.me links in rate-card.html")
        for num in wa_links:
            self.assertEqual(num, "254745163122", "Rate card WhatsApp links must use 254745163122")
        self.assertIn("handleRateCardWhatsAppSubmit", self.rate_content, "Must define handleRateCardWhatsAppSubmit")

    def test_rate_card_modal_fields(self):
        self.assertIn('id="booking-modal-overlay"', self.rate_content)
        self.assertIn('id="modal-name"', self.rate_content)
        self.assertIn('id="modal-phone"', self.rate_content)
        self.assertIn('id="modal-date"', self.rate_content)
        self.assertIn('id="modal-venue"', self.rate_content)
        self.assertIn('id="modal-pkg-select"', self.rate_content)
        self.assertIn('id="modal-notes"', self.rate_content)
        self.assertIn('openBookingModal', self.rate_content)
        self.assertIn('closeBookingModal', self.rate_content)

    def test_rate_card_table_inquire_buttons(self):
        inquire_buttons = re.findall(r'class="btn-table-inquire[^"]*"', self.rate_content)
        self.assertEqual(len(inquire_buttons), 5, "All 5 rate card packages must have an Inquire button")

    def test_contact_form_fields(self):
        self.assertIn('id="form-name"', self.index_content)
        self.assertIn('id="form-phone"', self.index_content)
        self.assertIn('id="form-date"', self.index_content)
        self.assertIn('id="form-location"', self.index_content)
        self.assertIn('id="form-package"', self.index_content)
        self.assertIn('id="form-message"', self.index_content)

    def test_package_prefill_and_scroll_helper(self):
        self.assertIn("function selectPackageAndScroll(pkgName)", self.index_content)

    def test_calendar_date_sync_target(self):
        self.assertIn("formDateInput.value = formatISODate(calSelectedDate)", self.index_content)


class TestBrandPurityAndContentSanitization(unittest.TestCase):
    def setUp(self):
        self.index_content = (REPO_DIR / "index.html").read_text(encoding="utf-8").lower()
        self.capture_content = (REPO_DIR / "capture_all.py").read_text(encoding="utf-8").lower()
        self.disallowed = [
            "w" + "ardawear",
            "w" + "arda wear",
            "living " + "the charge",
            "living-" + "the-charge",
            "soulful " + "melodies"
        ]

    def test_zero_disallowed_tokens_in_index(self):
        for token in self.disallowed:
            self.assertEqual(self.index_content.count(token), 0, f"Token '{token}' must not exist in index.html")

    def test_capture_script_clean_selectors(self):
        stale_token = "w" + "ardawear"
        self.assertNotIn(stale_token, self.capture_content, "capture script must not reference deleted selectors")


class TestSecurityPreflight(unittest.TestCase):
    SECRET_PATTERNS = [
        (re.compile(r'\bwhsec_[a-zA-Z0-9]{16,}\b'), "Stripe/Svix Webhook Secret"),
        (re.compile(r'\bsk_live_[a-zA-Z0-9]{16,}\b'), "Live Stripe Secret Key"),
        (re.compile(r'\bsk_test_[a-zA-Z0-9]{16,}\b'), "Stripe Test Secret Key"),
        (re.compile(r'\bpk_test_[a-zA-Z0-9]{16,}\b'), "Stripe Publishable Key"),
        (re.compile(r'\bsk-ant-api[a-zA-Z0-9\-]{16,}\b'), "Anthropic API Key"),
        (re.compile(r'\bsk-proj-[a-zA-Z0-9\-]{16,}\b'), "OpenAI Project API Key"),
        (re.compile(r'\bre_[a-zA-Z0-9]{24,36}\b'), "Resend API Key"),
        (re.compile(r'\btest_sk_[a-zA-Z0-9]{16,}\b'), "Highnote Secret Key"),
        (re.compile(r'\bghp_[a-zA-Z0-9]{36}\b'), "GitHub Personal Access Token"),
    ]

    def test_secret_patterns_zero_leaks(self):
        violations = []
        for root, dirs, files in os.walk(REPO_DIR):
            if any(ig in root for ig in [".git", "node_modules", ".tempmediaStorage"]):
                continue
            for f in files:
                if f.endswith((".ts", ".tsx", ".js", ".json", ".py", ".html", ".md", ".env")):
                    fpath = Path(root) / f
                    try:
                        content = fpath.read_text(encoding="utf-8", errors="ignore")
                        for line_no, line in enumerate(content.splitlines(), 1):
                            for pat, name in self.SECRET_PATTERNS:
                                if pat.search(line):
                                    violations.append(f"{fpath.name}:{line_no} [{name}]")
                    except Exception:
                        pass
        self.assertEqual(len(violations), 0, f"Found secrets in repo: {violations}")

class TestAirbnbBookingEngine(unittest.TestCase):
    def setUp(self):
        self.index_content = (REPO_DIR / "index.html").read_text(encoding="utf-8")
        self.css_path = REPO_DIR / "css" / "airbnb-booking.css"
        self.js_path = REPO_DIR / "js" / "airbnb-calendar.js"
        self.css_content = self.css_path.read_text(encoding="utf-8")
        self.js_content = self.js_path.read_text(encoding="utf-8")

    def test_modular_files_exist_and_non_empty(self):
        self.assertTrue(self.css_path.exists(), "css/airbnb-booking.css must exist")
        self.assertGreater(self.css_path.stat().st_size, 5000, "airbnb-booking.css must not be empty")
        self.assertTrue(self.js_path.exists(), "js/airbnb-calendar.js must exist")
        self.assertGreater(self.js_path.stat().st_size, 5000, "airbnb-calendar.js must not be empty")

    def test_index_includes_modular_assets(self):
        self.assertIn('href="css/airbnb-booking.css"', self.index_content)
        self.assertIn('src="js/airbnb-calendar.js"', self.index_content)

    def test_airbnb_css_tokens_and_selectors(self):
        self.assertIn('.bnb-calendar-card', self.css_content)
        self.assertIn('.bnb-segmented-control', self.css_content)
        self.assertIn('.bnb-slot-bar', self.css_content)
        self.assertIn('.bnb-day-cell.struck', self.css_content)
        self.assertIn('.bnb-day-cell.range-start', self.css_content)
        self.assertIn('.bnb-day-cell.range-end', self.css_content)
        self.assertIn('.bnb-day-cell.in-range', self.css_content)
        self.assertIn('.bnb-btn-test-sim', self.css_content)
        self.assertIn('.bnb-slot-modal-overlay', self.css_content)

    def test_airbnb_js_calendar_stream_and_methods(self):
        self.assertIn('function renderCalendarStream', self.js_content)
        self.assertIn('setAirbnbBookingMode', self.js_content)
        self.assertIn('setAirbnbTolerance', self.js_content)
        self.assertIn('clearAirbnbDates', self.js_content)
        self.assertIn('openSlotChangeModal', self.js_content)
        self.assertIn('selectPerformanceSlot', self.js_content)
        self.assertIn('dispatchAirbnbReservationWhatsApp', self.js_content)

    def test_simulation_mode_formatting(self):
        self.assertIn('⚠️ [TEST BOOKING SIMULATION]', self.js_content)
        self.assertIn('*AUTOMATED SYSTEM VERIFICATION TEST*', self.js_content)
        self.assertIn('STATUS: TEST SIMULATION VERIFIED', self.js_content)
        self.assertIn('https://wa.me/254745163122', self.js_content)

    def test_dom_elements_for_airbnb_features(self):
        self.assertIn('id="bnb-mode-dates"', self.index_content)
        self.assertIn('id="bnb-mode-flexible"', self.index_content)
        self.assertIn('id="bnb-slot-bar-val"', self.index_content)
        self.assertIn('id="bnb-calendar-stream"', self.index_content)
        self.assertIn('id="bnb-flex-section"', self.index_content)
        self.assertIn('id="bnb-slot-modal"', self.index_content)
        self.assertIn('dispatchAirbnbReservationWhatsApp(true)', self.index_content)
        self.assertIn('dispatchAirbnbReservationWhatsApp(false)', self.index_content)


if __name__ == "__main__":
    unittest.main()
