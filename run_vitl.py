#!/usr/bin/env python3
"""
VITL v2 (Vision-in-the-Loop) Automated Visual Testing & Evidence Capture
HERMES Layer 6 Verification Engine for Frederic Sax Ke Showcase
"""

import os
import time
import shutil
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By

REPO_DIR = Path(r"c:\Users\TATI\Desktop\Clients\October\Fred\Website Antigravity\SAX\SAX")
EVIDENCE_DIR = REPO_DIR / "EVIDENCE"
ARTIFACTS_DIR = Path(r"C:\Users\TATI\.gemini\antigravity\brain\6e20fdbe-5c76-4568-97a1-936f61bc4397")

EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

def save_and_copy(driver, filename):
    local_path = EVIDENCE_DIR / filename
    driver.save_screenshot(str(local_path))
    artifact_path = ARTIFACTS_DIR / filename
    shutil.copy2(str(local_path), str(artifact_path))
    print(f"[VITL] Captured: {filename} -> {local_path.stat().st_size} bytes")

def run_vitl():
    print("=" * 70)
    print("  EXECUTING HERMES VITL v2 — VISION-IN-THE-LOOP VISUAL AUDIT")
    print("=" * 70)

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    # ─────────────────────────────────────────────────────────────
    # PASS 1: DESKTOP VIEWPORT (1440 x 900)
    # ─────────────────────────────────────────────────────────────
    print("\n[+] PASS 1: Desktop Viewport (1440x900)...")
    options.add_argument("--window-size=1440,900")
    driver = webdriver.Edge(options=options)

    try:
        driver.get("http://localhost:8080")
        time.sleep(2)

        # 1. Desktop Hero
        save_and_copy(driver, "vitl_desktop_hero.png")

        # 2. Desktop Videos
        driver.execute_script("document.getElementById('videos').scrollIntoView({behavior: 'instant'});")
        time.sleep(1)
        save_and_copy(driver, "vitl_desktop_videos.png")

        # 3. Desktop Calendar
        driver.execute_script("document.getElementById('calendar').scrollIntoView({behavior: 'instant'});")
        time.sleep(1)
        # Click the 15th day cell or today to verify interactive focus
        driver.execute_script("""
            const openCells = document.querySelectorAll('.cal-day:not(.cal-past):not(.cal-empty)');
            if (openCells.length > 0) {
                openCells[Math.min(5, openCells.length - 1)].click();
            }
        """)
        time.sleep(1)
        save_and_copy(driver, "vitl_desktop_calendar.png")

        # 3b. Desktop Airbnb Sticky Card (Focused viewport)
        driver.execute_script("window.scrollBy({top: 250, behavior: 'instant'});")
        time.sleep(0.8)
        save_and_copy(driver, "vitl_desktop_airbnb_card.png")

        # 3c. Desktop Inclusions & Amenities Card
        driver.execute_script("""
            const am = document.querySelector('.airbnb-amenities-card');
            if (am) am.scrollIntoView({behavior: 'instant', block: 'center'});
        """)
        time.sleep(0.8)
        save_and_copy(driver, "vitl_desktop_amenities.png")

        # 4. Desktop Weddings
        driver.execute_script("document.getElementById('weddings').scrollIntoView({behavior: 'instant'});")
        time.sleep(1)
        save_and_copy(driver, "vitl_desktop_weddings.png")

        # 5. Desktop Rate Card Request Panel
        driver.execute_script("document.getElementById('ratecard').scrollIntoView({behavior: 'instant'});")
        time.sleep(1)
        save_and_copy(driver, "vitl_desktop_ratecard.png")

        # 6. Desktop Contracts & Invoice Portal
        driver.execute_script("document.getElementById('portal').scrollIntoView({behavior: 'instant'});")
        time.sleep(1)
        save_and_copy(driver, "vitl_desktop_portal.png")

        # 7. Dedicated Rate Card Page
        driver.get("http://localhost:8080/rate-card.html")
        time.sleep(1.5)
        save_and_copy(driver, "vitl_ratecard_page.png")

        # 7b. Interactive WhatsApp Booking Modal
        driver.execute_script("openBookingModal('Full Wedding Day Package');")
        time.sleep(1)
        save_and_copy(driver, "vitl_ratecard_modal.png")
        driver.execute_script("closeBookingModal();")
        time.sleep(0.5)

        # 7c. Dedicated Rate Card Terms & Booking
        driver.execute_script("document.querySelector('.notes-grid').scrollIntoView({behavior: 'instant'});")
        time.sleep(1)
        save_and_copy(driver, "vitl_ratecard_terms.png")

    finally:
        driver.quit()

    # ─────────────────────────────────────────────────────────────
    # PASS 2: MOBILE VIEWPORT (390 x 844 — iPhone 14/15)
    # ─────────────────────────────────────────────────────────────
    print("\n[+] PASS 2: Mobile Viewport (390x844)...")
    mob_options = Options()
    mob_options.add_argument("--headless=new")
    mob_options.add_argument("--disable-gpu")
    mob_options.add_argument("--no-sandbox")
    mob_options.add_argument("--window-size=390,844")
    mob_driver = webdriver.Edge(options=mob_options)

    try:
        mob_driver.get("http://localhost:8080")
        time.sleep(2)

        # 8. Mobile Hero
        save_and_copy(mob_driver, "vitl_mobile_hero.png")

        # 9. Mobile Navigation Drawer (Hamburger clicked)
        mob_driver.execute_script("""
            const btn = document.getElementById('hamburger-btn');
            if (btn) btn.click();
        """)
        time.sleep(0.8)
        save_and_copy(mob_driver, "vitl_mobile_drawer.png")

        # Close drawer and scroll to calendar
        mob_driver.execute_script("""
            if (typeof closeDrawer === 'function') closeDrawer();
            document.getElementById('calendar').scrollIntoView({behavior: 'instant'});
        """)
        time.sleep(1)
        # Select active slot chip
        mob_driver.execute_script("""
            const chips = document.querySelectorAll('.cal-slot-chip');
            if (chips.length > 1) chips[1].click();
        """)
        time.sleep(0.8)
        save_and_copy(mob_driver, "vitl_mobile_calendar.png")

        # 10. Mobile Reservation Card Focused
        mob_driver.execute_script("""
            const card = document.querySelector('.airbnb-reserve-card');
            if (card) card.scrollIntoView({behavior: 'instant'});
        """)
        time.sleep(0.8)
        save_and_copy(mob_driver, "vitl_mobile_reserve_card.png")

        # 11. Mobile Reservation CTA & Price Breakdown
        mob_driver.execute_script("""
            const btn = document.querySelector('.btn-airbnb-reserve');
            if (btn) btn.scrollIntoView({behavior: 'instant', block: 'center'});
        """)
        time.sleep(0.8)
        save_and_copy(mob_driver, "vitl_mobile_reserve_cta.png")

    finally:
        mob_driver.quit()

    print("\n" + "=" * 70)
    print("  HERMES VITL v2 COMPLETE — ALL EVIDENCE CAPTURED & DISTILLED")
    print("=" * 70)

if __name__ == "__main__":
    run_vitl()
