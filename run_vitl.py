#!/usr/bin/env python3
"""
VITL v3 (Vision-in-the-Loop) Automated Visual Testing & Evidence Capture Engine
HERMES Layer 6 Multi-Viewport Verification Engine for Frederic Sax Ke Luxury Showcase
Viewport Coverage:
- Desktop: 1440 x 900
- Tablet: 768 x 1024 (iPad Portrait)
- Mobile: 390 x 844 (iPhone 14/15)
"""

import os
import sys
import time
import shutil
import threading
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from selenium import webdriver
from selenium.webdriver.edge.options import Options

REPO_DIR = Path(r"c:\Users\TATI\Desktop\Clients\October\Fred\Website Antigravity\SAX\SAX")
EVIDENCE_DIR = REPO_DIR / "EVIDENCE"
ARTIFACTS_DIR = Path(r"C:\Users\TATI\.gemini\antigravity\brain\6e20fdbe-5c76-4568-97a1-936f61bc4397")

EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

class QuietHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def log_message(self, format, *args):
        pass  # Quiet logging

def start_local_server(port=8080):
    os.chdir(str(REPO_DIR))
    ThreadingHTTPServer.allow_reuse_address = True
    httpd = ThreadingHTTPServer(('127.0.0.1', port), QuietHandler)
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()
    return httpd

def save_and_copy(driver, filename):
    local_path = EVIDENCE_DIR / filename
    driver.save_screenshot(str(local_path))
    artifact_path = ARTIFACTS_DIR / filename
    shutil.copy2(str(local_path), str(artifact_path))
    print(f"[VITL] Captured: {filename} ({local_path.stat().st_size:,} bytes)")

def create_driver(width, height):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument(f"--window-size={width},{height}")
    return webdriver.Edge(options=options)

def run_vitl():
    print("=" * 70)
    print("  EXECUTING HERMES VITL v3 — VISION-IN-THE-LOOP MULTI-VIEWPORT AUDIT")
    print("=" * 70)

    server = start_local_server(8080)
    time.sleep(1)
    base_url = "http://127.0.0.1:8080"

    try:
        # ─────────────────────────────────────────────────────────────
        # PASS 1: DESKTOP VIEWPORT (1440 x 900)
        # ─────────────────────────────────────────────────────────────
        print("\n[+] PASS 1: Desktop Viewport (1440x900)...")
        driver_desktop = create_driver(1440, 900)
        try:
            driver_desktop.get(base_url)
            time.sleep(2)

            # 1. Desktop Hero
            save_and_copy(driver_desktop, "vitl_desktop_hero.png")

            # 2. Desktop Videos
            driver_desktop.execute_script("document.getElementById('videos').scrollIntoView({behavior: 'instant'});")
            time.sleep(1)
            save_and_copy(driver_desktop, "vitl_desktop_videos.png")

            # 3. Desktop Airbnb Continuous Calendar (Stream & Range Selection)
            driver_desktop.execute_script("document.getElementById('calendar').scrollIntoView({behavior: 'instant'});")
            time.sleep(1)
            save_and_copy(driver_desktop, "vitl_desktop_calendar.png")

            # 3b. Desktop Flexible Mode & Tolerance Chips
            driver_desktop.execute_script("""
                if (typeof setAirbnbBookingMode === 'function') {
                    setAirbnbBookingMode('flexible');
                }
            """)
            time.sleep(0.8)
            save_and_copy(driver_desktop, "vitl_desktop_airbnb_flexible.png")

            # 3c. Slot Selection Modal
            driver_desktop.execute_script("""
                if (typeof openSlotChangeModal === 'function') {
                    openSlotChangeModal();
                }
            """)
            time.sleep(0.8)
            save_and_copy(driver_desktop, "vitl_desktop_slot_modal.png")
            driver_desktop.execute_script("""
                if (typeof closeSlotChangeModal === 'function') {
                    closeSlotChangeModal();
                }
            """)
            time.sleep(0.5)

            # 3d. Desktop Sticky Reservation Card
            driver_desktop.execute_script("""
                const card = document.querySelector('.airbnb-reserve-card');
                if (card) card.scrollIntoView({behavior: 'instant', block: 'center'});
            """)
            time.sleep(0.8)
            save_and_copy(driver_desktop, "vitl_desktop_airbnb_card.png")

            # 3e. Inclusions & Amenities Card
            driver_desktop.execute_script("""
                const am = document.querySelector('.airbnb-amenities-card');
                if (am) am.scrollIntoView({behavior: 'instant', block: 'center'});
            """)
            time.sleep(0.8)
            save_and_copy(driver_desktop, "vitl_desktop_amenities.png")

            # 4. Desktop Weddings
            driver_desktop.execute_script("document.getElementById('weddings').scrollIntoView({behavior: 'instant'});")
            time.sleep(1)
            save_and_copy(driver_desktop, "vitl_desktop_weddings.png")

            # 5. Desktop Rate Card Request Panel
            driver_desktop.execute_script("document.getElementById('ratecard').scrollIntoView({behavior: 'instant'});")
            time.sleep(1)
            save_and_copy(driver_desktop, "vitl_desktop_ratecard.png")

            # 6. Desktop Client Portal (Contracts & Invoice)
            driver_desktop.execute_script("document.getElementById('portal').scrollIntoView({behavior: 'instant'});")
            time.sleep(1)
            save_and_copy(driver_desktop, "vitl_desktop_portal.png")

            # 7. Dedicated Rate Card Page
            driver_desktop.get(f"{base_url}/rate-card.html")
            time.sleep(1.5)
            save_and_copy(driver_desktop, "vitl_ratecard_page.png")

            # 7b. Interactive WhatsApp Booking Modal
            driver_desktop.execute_script("openBookingModal('Full Wedding Day Package');")
            time.sleep(1)
            save_and_copy(driver_desktop, "vitl_ratecard_modal.png")
            driver_desktop.execute_script("closeBookingModal();")
            time.sleep(0.5)

            # 7c. Dedicated Rate Card Terms & Booking
            driver_desktop.execute_script("document.querySelector('.notes-grid').scrollIntoView({behavior: 'instant'});")
            time.sleep(1)
            save_and_copy(driver_desktop, "vitl_ratecard_terms.png")

        finally:
            driver_desktop.quit()

        # ─────────────────────────────────────────────────────────────
        # PASS 2: TABLET VIEWPORT (768 x 1024 — iPad Portrait)
        # ─────────────────────────────────────────────────────────────
        print("\n[+] PASS 2: Tablet Viewport (768x1024)...")
        driver_tablet = create_driver(768, 1024)
        try:
            driver_tablet.get(base_url)
            time.sleep(2)

            driver_tablet.execute_script("document.getElementById('calendar').scrollIntoView({behavior: 'instant'});")
            time.sleep(1)
            save_and_copy(driver_tablet, "vitl_tablet_calendar.png")

            driver_tablet.execute_script("""
                const card = document.querySelector('.airbnb-reserve-card');
                if (card) card.scrollIntoView({behavior: 'instant', block: 'center'});
            """)
            time.sleep(0.8)
            save_and_copy(driver_tablet, "vitl_tablet_card.png")
        finally:
            driver_tablet.quit()

        # ─────────────────────────────────────────────────────────────
        # PASS 3: MOBILE VIEWPORT (390 x 844 — iPhone 14/15)
        # ─────────────────────────────────────────────────────────────
        print("\n[+] PASS 3: Mobile Viewport (390x844)...")
        driver_mobile = create_driver(390, 844)
        try:
            driver_mobile.get(base_url)
            time.sleep(2)

            # 8. Mobile Hero
            save_and_copy(driver_mobile, "vitl_mobile_hero.png")

            # 9. Mobile Navigation Drawer
            driver_mobile.execute_script("""
                const btn = document.getElementById('hamburger-btn');
                if (btn) btn.click();
            """)
            time.sleep(0.8)
            save_and_copy(driver_mobile, "vitl_mobile_drawer.png")

            # Close drawer and scroll to calendar
            driver_mobile.execute_script("""
                if (typeof closeDrawer === 'function') closeDrawer();
                document.getElementById('calendar').scrollIntoView({behavior: 'instant'});
            """)
            time.sleep(1)

            # 10. Mobile Continuous Calendar Stream
            save_and_copy(driver_mobile, "vitl_mobile_calendar.png")

            # 11. Mobile Flexible Mode & Tolerance Chips
            driver_mobile.execute_script("""
                if (typeof setAirbnbBookingMode === 'function') {
                    setAirbnbBookingMode('flexible');
                }
                const bbar = document.querySelector('.bnb-bottom-bar');
                if (bbar) bbar.scrollIntoView({behavior: 'instant', block: 'center'});
            """)
            time.sleep(0.8)
            save_and_copy(driver_mobile, "vitl_mobile_airbnb_flexible.png")

            # 12. Mobile Slot Modal
            driver_mobile.execute_script("""
                if (typeof openSlotChangeModal === 'function') {
                    openSlotChangeModal();
                }
            """)
            time.sleep(0.8)
            save_and_copy(driver_mobile, "vitl_mobile_slot_modal.png")
            driver_mobile.execute_script("""
                if (typeof closeSlotChangeModal === 'function') {
                    closeSlotChangeModal();
                }
            """)
            time.sleep(0.5)

            # 13. Mobile Reservation Card & Simulation Button
            driver_mobile.execute_script("""
                const card = document.querySelector('.airbnb-reserve-card');
                if (card) card.scrollIntoView({behavior: 'instant', block: 'center'});
            """)
            time.sleep(0.8)
            save_and_copy(driver_mobile, "vitl_mobile_reserve_card.png")

            # 14. Mobile WhatsApp CTA Buttons
            driver_mobile.execute_script("""
                const btn = document.querySelector('.btn-airbnb-reserve');
                if (btn) btn.scrollIntoView({behavior: 'instant', block: 'center'});
            """)
            time.sleep(0.8)
            save_and_copy(driver_mobile, "vitl_mobile_reserve_cta.png")

        finally:
            driver_mobile.quit()

    finally:
        server.shutdown()
        server.server_close()

    print("\n" + "=" * 70)
    print("  HERMES VITL v3 COMPLETE — ALL EVIDENCE CAPTURED & DISTILLED")
    print("=" * 70)

if __name__ == "__main__":
    run_vitl()
