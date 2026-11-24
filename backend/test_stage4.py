"""
Stage 4 Frontend & Backend Integration Test Suite.

Verifies:
1. Dynamic content hydration endpoint (/api/v1/content) provides all 11 sections.
2. Exact DOM selectors match 1:1 between backend seed data and frontend index.html.
3. Simulated full client DOM hydration (services, why-us, steps, cases, faq, contacts).
4. ETag validation and 304 Not Modified caching for content hydration.
5. Real lead submission matching frontend `modals.js` payload.
6. Honeypot anti-spam trap (silent rejection of automated form submissions).
7. Rate limiting on lead creation (protection against form flooding).
8. Static frontend integrity (honeypot fields, privacy policy links in dist/ and index.html).
"""

import json
from pathlib import Path
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient
from app.config import settings
from app.main import app

client = TestClient(app)

print("=" * 60)
print("  ЭТАП 4: ГЕНЕРАЛЬНАЯ ПРОВЕРКА СВЯЗКИ ФРОНТЕНДА И БЭКЕНДА")
print("=" * 60)

# TEST 1: Hydration Endpoint Completeness
print("\n[TEST 1] Проверка эндпоинта гидрации (/api/v1/content)...")
r_content = client.get("/api/v1/content")
assert r_content.status_code == 200, f"Expected 200, got {r_content.status_code}"
content_data = r_content.json()
assert "sections" in content_data, "Missing 'sections' in content response"
sections = content_data["sections"]

required_sections = [
    "header", "hero", "expertise", "services", "why_us",
    "steps", "sectors", "engineer_cta", "cases", "faq", "contacts"
]
for sec in required_sections:
    assert sec in sections, f"Section '{sec}' missing in /api/v1/content response!"
print(f"  ✓ Все 11 секций присутствуют в ответе API для гидрации фронтенда")

# TEST 2: Full DOM Hydration Simulation
print("\n[TEST 2] Проверка сквозной гидрации DOM-дерева лендинга...")
root_dir = Path(__file__).resolve().parent.parent
dist_index = root_dir / "dist" / "index.html"
soup = BeautifulSoup(dist_index.read_text(encoding="utf-8"), "html.parser")

# 1. Services
services_cards = soup.select("#services .service-card-stagger")
assert len(services_cards) == 7, f"Expected 7 service cards in DOM, found {len(services_cards)}"
assert len(sections["services"]["items"]) == 7, f"Expected 7 services in DB, found {len(sections['services']['items'])}"

# 2. Why Us
why_us_odometers = soup.select("#why-us .stat-odometer")
assert len(why_us_odometers) == 3, f"Expected 3 odometers in #why-us, found {len(why_us_odometers)}"
assert len(sections["why_us"]["items"]) == 3, f"Expected 3 why_us items in DB, found {len(sections['why_us']['items'])}"

# 3. Steps
step_titles = soup.select("#steps h3.step-title")
assert len(step_titles) == 5, f"Expected 5 step titles in #steps, found {len(step_titles)}"
assert len(sections["steps"]["items"]) == 5, f"Expected 5 steps in DB, found {len(sections['steps']['items'])}"

# 4. Cases
cases_headings = soup.select("#cases h3")
assert len(cases_headings) >= 3, f"Expected at least 3 case cards in #cases, found {len(cases_headings)}"

# 5. FAQ
faq_rows = soup.select("#faq .faq-row")
assert len(faq_rows) == 5, f"Expected 5 FAQ rows in #faq, found {len(faq_rows)}"
assert len(sections["faq"]["items"]) == 5, f"Expected 5 FAQ items in DB, found {len(sections['faq']['items'])}"

# 6. Contacts & Legal
assert soup.select_one("#header [data-header-hours]") is not None, "Missing [data-header-hours] in header"
assert soup.select_one("#footer [data-footer-address]") is not None, "Missing [data-footer-address] in footer"
assert soup.select_one("#footer [data-footer-hours]") is not None, "Missing [data-footer-hours] in footer"
assert soup.select_one("#footer [data-footer-inn]") is not None, "Missing [data-footer-inn] in footer"
print("  ✓ Селекторы фронтенда и структура бэкенда синхронизированы на 100% (7 услуг, 3 метрики, 5 этапов, 5 FAQ)")

# TEST 3: Caching and Conditional GET (ETag / 304)
print("\n[TEST 3] Проверка ETag и 304 Not Modified для контент-лоадера...")
etag = r_content.headers.get("etag")
assert etag is not None, "ETag header missing in content response"

r_conditional = client.get("/api/v1/content", headers={"If-None-Match": etag})
assert r_conditional.status_code == 304, f"Expected 304 Not Modified, got {r_conditional.status_code}"
assert len(r_conditional.content) == 0, "304 response should not contain body payload"
print(f"  ✓ Условный запрос с ETag ({etag}) корректно возвращает HTTP 304 (0 байт трафика)")

# TEST 4: Real Lead Submission (matching modals.js)
print("\n[TEST 4] Проверка отправки реальной заявки с фронтенда (модалка и форма секции 07)...")
lead_payload = {
    "name": "Валентин Тимлид",
    "phone": "+7 (914) 792-56-40",
    "source": "section07_engineer",
    "company_website": None
}
r_lead = client.post("/api/v1/leads", json=lead_payload)
assert r_lead.status_code == 200, f"Lead submission failed: {r_lead.status_code}"
lead_res = r_lead.json()
assert lead_res["status"] == "success"
lead_id = lead_res["lead_id"]
print(f"  ✓ Заявка успешно принята сервером, присвоен ID #{lead_id}")

# Verify in Admin API
r_login = client.post("/api/v1/auth/login", json={"username": "admin", "password": settings.DEFAULT_ADMIN_PASSWORD})
auth_token = r_login.json()["access_token"]
auth_header = {"Authorization": f"Bearer {auth_token}"}

r_check = client.get("/api/v1/admin/leads", headers=auth_header)
saved_lead = next((l for l in r_check.json()["leads"] if l["id"] == lead_id), None)
assert saved_lead is not None, f"Lead #{lead_id} not found in database"
assert saved_lead["name"] == "Валентин Тимлид"
assert saved_lead["phone"] == "+7 (914) 792-56-40"
assert saved_lead["source"] == "section07_engineer"
assert saved_lead["status"] == "new"
print(f"  ✓ Данные заявки #{lead_id} сохранены в БД с корректными полями")

# Cleanup lead
client.delete(f"/api/v1/admin/leads/{lead_id}", headers=auth_header)

# TEST 5: Honeypot Anti-Spam Trap
print("\n[TEST 5] Проверка Honeypot-ловушки для спам-ботов...")
bot_payload = {
    "name": "Spam Bot",
    "phone": "+7 (999) 000-00-00",
    "source": "modal_popup",
    "company_website": "https://fast-seo-boost.com/buy"
}
r_bot = client.post("/api/v1/leads", json=bot_payload)
assert r_bot.status_code == 200, "Honeypot should respond 200 to not alert the bot"

# Verify that bot lead was NOT saved to the database
r_check_bot = client.get("/api/v1/admin/leads", headers=auth_header)
bot_leads = [l for l in r_check_bot.json()["leads"] if l["name"] == "Spam Bot"]
assert len(bot_leads) == 0, "Bot submission bypassed honeypot and was saved to DB!"
print("  ✓ Спам-бот тихо пойман в honeypot-ловушку: ответ HTTP 200, в БД ничего не записано")

# TEST 6: Rate Limiting on Form Submissions
print("\n[TEST 6] Проверка защиты от флуда формами (Rate Limit: 5 в минуту)...")
test_ip_headers = {"X-Forwarded-For": "203.0.113.88"}

flood_lead_ids = []
for i in range(5):
    r_flood = client.post("/api/v1/leads", json={
        "name": f"User {i}",
        "phone": "+7 (914) 111-22-33",
        "source": "flood_test"
    }, headers=test_ip_headers)
    assert r_flood.status_code == 200
    if "lead_id" in r_flood.json():
        flood_lead_ids.append(r_flood.json()["lead_id"])

# 6th request must be rate limited
r_limited = client.post("/api/v1/leads", json={
    "name": "User Flooder",
    "phone": "+7 (914) 111-22-33",
    "source": "flood_test"
}, headers=test_ip_headers)

assert r_limited.status_code == 429, f"Expected 429, got {r_limited.status_code}"
assert "Слишком много запросов" in r_limited.json().get("detail", "") or "Слишком много запросов" in r_limited.json().get("message", "")
print("  ✓ Лимит 5 заявок в минуту с одного IP работает: 6-й запрос заблокирован (HTTP 429)")

# Clean up flood leads
for f_id in flood_lead_ids:
    client.delete(f"/api/v1/admin/leads/{f_id}", headers=auth_header)

# TEST 7: Static Frontend Integrity (dist/ & index.html)
print("\n[TEST 7] Проверка разметки фронтенда на соответствие требованиям прода...")
index_path = root_dir / "index.html"
dist_index_path = root_dir / "dist" / "index.html"

assert index_path.exists(), "Root index.html missing!"
assert dist_index_path.exists(), "dist/index.html missing! Run 'npm run build'."

index_content = index_path.read_text(encoding="utf-8")
dist_content = dist_index_path.read_text(encoding="utf-8")

# Check honeypot field
assert 'name="company_website"' in index_content, "Honeypot field missing in index.html"
assert 'name="company_website"' in dist_content, "Honeypot field missing in dist/index.html"

# Check privacy policy links
assert '/privacy.html' in index_content, "Privacy policy link missing in index.html"
assert '/privacy.html' in dist_content, "Privacy policy link missing in dist/index.html"

# Check phone input mask validation attributes
assert 'id="consult-phone"' in index_content
assert 'id="modal-lead-phone"' in index_content
print("  ✓ Фронтенд (исходник и production build в dist/) содержит все необходимые поля и ссылки")

print("\n" + "=" * 60)
print("  🎉 ВСЕ ТЕСТЫ ЭТАПА 4 УСПЕШНО ПРОЙДЕНЫ! 🎉")
print("=" * 60)
