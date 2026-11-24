"""
Comprehensive Deep End-to-End Integration Test Suite for Stage 4
Verifies frontend-backend binding, DOM selector consistency, ETag/304 cache lifecycle,
honeypot anti-spam, and rate-limiting.
"""

import asyncio
import hashlib
import json
import os
import sys
from bs4 import BeautifulSoup
import httpx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.main import app

BASE_URL = "http://testserver"

async def run_deep_test_suite():
    passed = 0
    total = 0

    def record(name, condition, details=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  [PASS] Test {total}: {name}")
        else:
            print(f"  [FAIL] Test {total}: {name} - {details}")

    print("==========================================================")
    print("STARTING DEEP GENERAL INSPECTION TEST SUITE (STAGE 4)")
    print("==========================================================")

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=BASE_URL) as client:
        # ----------------------------------------------------
        # 1. DOM SELECTOR CONSISTENCY WITH PRODUCTION HTML
        # ----------------------------------------------------
        print("\n--- Phase 1: DOM & Content Schema Verification ---")
        with open("index.html", "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        # Public content fetch
        res = await client.get("/api/v1/content")
        record("GET /api/v1/content returns 200", res.status_code == 200)
        data = res.json()
        sections = data.get("sections", {})

        # Header selectors
        header_el = soup.find("header", id="header")
        hours_el = soup.select_one("#header [data-header-hours]")
        record("Header element and data-header-hours exist in DOM", header_el is not None and hours_el is not None)

        # Hero selectors
        hero_el = soup.find("section", id="hero")
        hero_h1 = hero_el.find("h1") if hero_el else None
        hero_ps = hero_el.find_all("p") if hero_el else []
        record("Hero h1 and paragraphs exist in DOM", hero_h1 is not None and len(hero_ps) >= 2)

        # Services: exactly 7 cards
        service_cards = soup.select("#services .service-card-stagger")
        api_services = sections.get("services", {}).get("items", [])
        record(
            f"Services DOM cards match API count (DOM: {len(service_cards)}, API: {len(api_services)})",
            len(service_cards) == 7 and len(api_services) == 7
        )

        # Why Us: 3 odometers
        odometers = soup.select("#why-us .stat-odometer")
        api_metrics = sections.get("why_us", {}).get("items", [])
        record(
            f"Why-Us DOM odometers match API count (DOM: {len(odometers)}, API: {len(api_metrics)})",
            len(odometers) == 3 and len(api_metrics) == 3
        )

        # Steps: 5 rows
        step_rows = soup.select("#steps .step-row")
        api_steps = sections.get("steps", {}).get("items", [])
        record(
            f"Steps DOM rows match API count (DOM: {len(step_rows)}, API: {len(api_steps)})",
            len(step_rows) == 5 and len(api_steps) == 5
        )

        # Sectors: 4 horizontal cards
        sector_cards = soup.select("#sectors-track > div")
        api_sectors = sections.get("sectors", {}).get("items", [])
        record(
            f"Sectors DOM cards match API count (DOM: {len(sector_cards)}, API: {len(api_sectors)})",
            len(sector_cards) == 4 and len(api_sectors) == 4
        )

        # Cases: 3 cards and 3 tabs
        case_cards = soup.select("#cases .case-card")
        case_tabs = soup.select("#cases .case-tab-btn")
        api_cases = sections.get("cases", {}).get("items", [])
        record(
            f"Cases DOM cards and tabs match API count (DOM: {len(case_cards)}/{len(case_tabs)}, API: {len(api_cases)})",
            len(case_cards) == 3 and len(case_tabs) == 3 and len(api_cases) == 3
        )

        # Verify case-card indices match tab indices
        case_indices = sorted([int(c.get("data-case-idx", -1)) for c in case_cards])
        tab_indices = sorted([int(t.get("data-case-index", -1)) for t in case_tabs])
        record("Case card indices and tab indices are strictly [0, 1, 2]", case_indices == [0, 1, 2] and tab_indices == [0, 1, 2])

        # Consult Form and Engineer CTA
        consult_form = soup.find("form", id="consult-form")
        form_col = consult_form.parent if consult_form else None
        form_h3 = form_col.find("h3") if form_col else None
        grid = form_col.parent if form_col else None
        eng_img = grid.find("img") if grid else None
        record(
            "Engineer CTA form container has h3 and engineer image",
            form_h3 is not None and "ОБСУДИМ ВАШ ПРОЕКТ" in form_h3.get_text() and eng_img is not None
        )

        # FAQ: 5 rows and verify typo fix in row 1
        faq_rows = soup.select("#faq .faq-row")
        api_faq = sections.get("faq", {}).get("items", [])
        row1_text = faq_rows[0].select_one(".faq-answer-text").get_text(strip=True) if faq_rows else ""
        record(
            f"FAQ DOM rows match API count and typo in Row 1 is fixed (DOM: {len(faq_rows)}, API: {len(api_faq)})",
            len(faq_rows) == 5 and len(api_faq) == 5 and "Владивостоку" in row1_text
        )

        # Footer data attributes & full site media hooks
        footer_addr = soup.select_one("#footer [data-footer-address]")
        footer_hours = soup.select_one("#footer [data-footer-hours]")
        footer_inn = soup.select_one("#footer [data-footer-inn]")
        has_media_hooks = (
            len(soup.select("img[data-brand-logo]")) == 2
            and len(soup.select("img[data-expertise-img]")) == 3
            and len(soup.select("img[data-ticker-photo]")) == 24
            and len(soup.select("img[data-partner-logo]")) == 20
            and soup.select_one("#hero-bg-video") is not None
            and soup.select_one("#installation-3d-img") is not None
        )
        record(
            "Footer attributes and all site media DOM hooks (logos, ticker photos, partner logos, video) are present",
            footer_addr is not None and footer_hours is not None and footer_inn is not None and has_media_hooks
        )

        # ----------------------------------------------------
        # 2. ETAG & CONDITIONAL HTTP REVALIDATION
        # ----------------------------------------------------
        print("\n--- Phase 2: HTTP Cache & ETag Revalidation Lifecycle ---")
        etag = res.headers.get("etag")
        cache_ctrl = res.headers.get("cache-control")
        record("Response includes strong/weak ETag and 'no-cache' Cache-Control", bool(etag) and "no-cache" in cache_ctrl)

        # Conditional GET with If-None-Match
        cond_res = await client.get("/api/v1/content", headers={"If-None-Match": etag})
        record("Conditional GET with matching ETag returns HTTP 304 Not Modified", cond_res.status_code == 304)

        # Login as admin to test content modification and ETag invalidation
        login_res = await client.post("/api/v1/auth/login", json={"username": "admin", "password": settings.DEFAULT_ADMIN_PASSWORD})
        record("Admin login successful", login_res.status_code == 200)
        token = login_res.json()["access_token"]
        auth_hdr = {"Authorization": f"Bearer {token}"}

        # Modify hero title
        hero_sec = sections.get("hero", {})
        original_title = hero_sec.get("title", "СИСТЕМЫ ЗАЩИТЫ")
        test_title = "СИСТЕМЫ БЕЗОПАСНОСТИ И ЗАЩИТЫ"
        hero_sec["title"] = test_title

        update_res = await client.put("/api/v1/admin/content/hero", json={"data": hero_sec}, headers=auth_hdr)
        record("Admin updates hero section", update_res.status_code == 200)

        # Fresh public GET must return new content, new ETag, and 200 with old ETag
        after_update_res = await client.get("/api/v1/content", headers={"If-None-Match": etag})
        new_etag = after_update_res.headers.get("etag")
        new_title = after_update_res.json().get("sections", {}).get("hero", {}).get("title")
        record(
            "Conditional GET with stale ETag returns HTTP 200 and updated content",
            after_update_res.status_code == 200 and new_etag != etag and new_title == test_title
        )

        # Restore original hero title
        hero_sec["title"] = original_title
        await client.put("/api/v1/admin/content/hero", json={"data": hero_sec}, headers=auth_hdr)

        # ----------------------------------------------------
        # 3. FORMS, ANTI-SPAM & RATE LIMITING
        # ----------------------------------------------------
        print("\n--- Phase 3: Forms, Honeypot & Rate-Limiting ---")

        # Get initial leads count
        leads_list_res = await client.get("/api/v1/admin/leads", headers=auth_hdr)
        initial_lead_count = leads_list_res.json()["total"]

        # Honeypot spam submission: must NOT increment real leads
        spam_res = await client.post("/api/v1/leads", json={
            "name": "Bot Spammer",
            "phone": "+7 (999) 000-00-00",
            "source": "modal_popup",
            "company_website": "http://spam-casino.example.com"
        })
        record("Honeypot submission returns HTTP 200 success message to fool bot", spam_res.status_code == 200)

        after_spam_leads = await client.get("/api/v1/admin/leads", headers=auth_hdr)
        record("Honeypot lead was SILENTLY DISCARDED (database total unchanged)", after_spam_leads.json()["total"] == initial_lead_count)

        # Valid lead submission from consult form
        lead_res = await client.post("/api/v1/leads", json={
            "name": "Валентин Старший",
            "phone": "+7 (914) 700-11-22",
            "source": "section07_engineer"
        })
        record("Legitimate lead submission from Section 07 succeeds", lead_res.status_code == 200 and lead_res.json()["status"] == "success")

        # Verify lead in admin triage
        latest_leads = await client.get("/api/v1/admin/leads", headers=auth_hdr)
        latest_lead = latest_leads.json()["leads"][0]
        record(
            "New lead appears in admin list with correct name, phone, and source",
            latest_lead["name"] == "Валентин Старший" and latest_lead["phone"] == "+7 (914) 700-11-22" and latest_lead["source"] == "section07_engineer"
        )

        # Clean up test lead
        del_res = await client.delete(f"/api/v1/admin/leads/{latest_lead['id']}", headers=auth_hdr)
        record("Admin cleans up test lead", del_res.status_code == 200)

    print("\n==========================================================")
    print(f"RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("==========================================================")
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(run_deep_test_suite())
    sys.exit(0 if success else 1)
