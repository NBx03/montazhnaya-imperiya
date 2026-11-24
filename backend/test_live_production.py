"""
Live Production Verification Test Suite for https://montazh.documentics.ru
Validates live HTTPS deployment, Caddy reverse-proxy, SSL certificate,
FastAPI backend daemon, Admin panel, dynamic content hydration, ETag 304,
honeypot anti-spam, and lead processing on the real server.
"""

import hashlib
import json
import os
import sys
from pathlib import Path
import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))
from app.config import settings

LIVE_URL = os.getenv("LIVE_URL", "https://montazh.documentics.ru")

def run_live_tests():
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

    print("============================================================")
    print("  БОЕВАЯ ВЕРИФИКАЦИЯ ПРОДАКШЕНА: https://montazh.documentics.ru")
    print("============================================================")

    with httpx.Client(base_url=LIVE_URL, timeout=15.0, follow_redirects=True) as client:
        # ----------------------------------------------------
        # 1. SSL & Security Headers on Root Landing Page
        # ----------------------------------------------------
        print("\n[1] Проверка главной страницы и HTTPS...")
        res_root = client.get("/")
        record("Главная страница открывается по HTTPS (HTTP 200)", res_root.status_code == 200)
        
        headers = res_root.headers
        record("Заголовок HSTS включен", "strict-transport-security" in headers)
        record("Заголовок X-Content-Type-Options: nosniff", headers.get("x-content-type-options") == "nosniff")
        record("Заголовок X-Frame-Options: SAMEORIGIN", headers.get("x-frame-options") == "SAMEORIGIN")
        record("Баннер Server скрыт (-Server)", "caddy" not in headers.get("server", "").lower())
        record("HTML содержит корневой заголовок 'СИСТЕМЫ ЗАЩИТЫ'", "СИСТЕМЫ ЗАЩИТЫ" in res_root.text)

        # ----------------------------------------------------
        # 2. Clean URLs & 152-ФЗ Privacy Page
        # ----------------------------------------------------
        print("\n[2] Проверка страницы политики конфиденциальности (Clean URLs)...")
        res_privacy_clean = client.get("/privacy")
        res_privacy_html = client.get("/privacy.html")
        record("Clean URL /privacy отдает страницу (HTTP 200)", res_privacy_clean.status_code == 200)
        record("Прямой URL /privacy.html отдает страницу (HTTP 200)", res_privacy_html.status_code == 200)
        record("Страница содержит регламент 152-ФЗ и реквизиты", "152-ФЗ" in res_privacy_clean.text and "Монтажная Империя" in res_privacy_clean.text)

        # ----------------------------------------------------
        # 3. Public API & ETag 304 Lifecycle
        # ----------------------------------------------------
        print("\n[3] Проверка публичного API контента (/api/v1/content)...")
        res_content = client.get("/api/v1/content")
        record("GET /api/v1/content возвращает HTTP 200", res_content.status_code == 200)
        content_json = res_content.json()
        sections = content_json.get("sections", {})
        record(f"API отдает все 11 секций сайта (получено: {len(sections)})", len(sections) == 11)

        etag = res_content.headers.get("etag")
        record("Ответ содержит валидный ETag", bool(etag))

        # Conditional GET
        res_304 = client.get("/api/v1/content", headers={"If-None-Match": etag})
        record("Условный GET с If-None-Match возвращает HTTP 304 Not Modified", res_304.status_code == 304)

        # ----------------------------------------------------
        # 4. Admin Panel Static Assets & Authentication
        # ----------------------------------------------------
        print("\n[4] Проверка админ-панели и авторизации...")
        res_admin = client.get("/admin/")
        record("SPA Админка открывается по /admin/ (HTTP 200)", res_admin.status_code == 200)
        record("Админка содержит скрипт admin.js", "admin.js" in res_admin.text)

        res_admin_js = client.get("/admin/admin.js")
        record("Статика admin.js отдается сервером (HTTP 200)", res_admin_js.status_code == 200)

        # Login with production credentials (from environment or local .env settings)
        login_payload = {
            "username": os.getenv("LIVE_ADMIN_USERNAME", settings.DEFAULT_ADMIN_USERNAME),
            "password": os.getenv("LIVE_ADMIN_PASSWORD", settings.DEFAULT_ADMIN_PASSWORD),
        }
        res_login = client.post("/api/v1/auth/login", json=login_payload)
        record("Авторизация администратора успешна (HTTP 200)", res_login.status_code == 200)
        token = res_login.json().get("access_token")
        record("Получен рабочий Bearer JWT токен", bool(token))
        auth_hdr = {"Authorization": f"Bearer {token}"}

        # ----------------------------------------------------
        # 5. Lead Submission, Anti-Spam & Admin Triage Cycle
        # ----------------------------------------------------
        print("\n[5] Проверка отправки заявок и анти-спама...")
        # Honeypot submission
        res_spam = client.post("/api/v1/leads", json={
            "name": "Live Bot Spammer",
            "phone": "+7 (999) 000-11-22",
            "source": "live_test",
            "company_website": "http://spambot-trap.com"
        })
        record("Honeypot-заявка возвращает 200 (тихий отсев)", res_spam.status_code == 200)

        # Real lead submission from landing page
        res_lead = client.post("/api/v1/leads", json={
            "name": "Проверочный Заказчик",
            "phone": "+7 (914) 777-88-99",
            "source": "modal_popup"
        })
        record("Реальная заявка успешно создана на боевом сервере (HTTP 200)", res_lead.status_code == 200 and res_lead.json().get("status") == "success")

        # Admin checks lead list
        res_leads_admin = client.get("/api/v1/admin/leads", headers=auth_hdr)
        leads_list = res_leads_admin.json().get("leads", [])
        record("Администратор видит созданную заявку в дашборде", len(leads_list) > 0 and leads_list[0]["phone"] == "+7 (914) 777-88-99")

        # Clean up test lead to leave database pristine
        if leads_list:
            lead_id = leads_list[0]["id"]
            res_del = client.delete(f"/api/v1/admin/leads/{lead_id}", headers=auth_hdr)
            record("Тестовая заявка удалена из боевой базы данных (БД чиста)", res_del.status_code == 200)

        # ----------------------------------------------------
        # 6. Immutable Cache for Hashed Vite Assets
        # ----------------------------------------------------
        print("\n[6] Проверка кеширования ассетов...")
        # Find asset path in root HTML
        import re
        asset_match = re.search(r'/assets/main-[a-zA-Z0-9_-]+\.js', res_root.text)
        if asset_match:
            asset_url = asset_match.group(0)
            res_asset = client.get(asset_url)
            asset_cache = res_asset.headers.get("cache-control", "")
            record(f"Vite bundle {asset_url} имеет immutable-кеш ({asset_cache})", "immutable" in asset_cache)
        else:
            record("Найдена ссылка на Vite bundle в HTML", False, "Не удалось найти путь к /assets/main-*.js")

        # ----------------------------------------------------
        # 7. SEO Assets & Error Handling (Favicon, Robots, Sitemap, 404)
        # ----------------------------------------------------
        print("\n[7] Проверка SEO-ассетов и обработки ошибок...")
        res_fav = client.get("/favicon.ico")
        record("GET /favicon.ico возвращает валидную иконку (HTTP 200)", res_fav.status_code == 200 and "image" in res_fav.headers.get("content-type", ""))

        res_robots = client.get("/robots.txt")
        record("GET /robots.txt возвращает файл индексации с Disallow /admin/ (HTTP 200)", res_robots.status_code == 200 and "Disallow: /admin/" in res_robots.text)

        res_sitemap = client.get("/sitemap.xml")
        record("GET /sitemap.xml возвращает валидный XML sitemap (HTTP 200)", res_sitemap.status_code == 200 and "<urlset" in res_sitemap.text)

        res_404 = client.get("/nonexistent-page-audit-check-404")
        record("Несуществующий URL возвращает HTTP 404", res_404.status_code == 404)
        record("Ответ 404 содержит фирменную страницу 'Страница не найдена'", "Страница не найдена" in res_404.text)

        # ----------------------------------------------------
        # 8. API Documentation & OpenAPI Specs
        # ----------------------------------------------------
        print("\n[8] Проверка документации API (Swagger UI / OpenAPI)...")
        res_docs = client.get("/docs")
        record("GET /docs отдает интерфейс Swagger UI (HTTP 200)", res_docs.status_code == 200 and "swagger-ui" in res_docs.text.lower())

        res_openapi = client.get("/openapi.json")
        openapi_data = res_openapi.json() if res_openapi.status_code == 200 else {}
        record("GET /openapi.json отдает спецификацию OpenAPI (HTTP 200)", res_openapi.status_code == 200 and "Монтажная Империя" in openapi_data.get("info", {}).get("title", ""))

        # ----------------------------------------------------
        # 9. Admin CSV Export & Security Hardening
        # ----------------------------------------------------
        print("\n[9] Проверка выгрузки отчетов, валидации и медиа-библиотеки...")
        res_csv = client.get("/api/v1/admin/leads/export-csv", headers=auth_hdr)
        record("Выгрузка CSV отдает корректный заголовок text/csv (HTTP 200)", res_csv.status_code == 200 and "text/csv" in res_csv.headers.get("content-type", ""))
        record("CSV содержит UTF-8 BOM и корректные колонки", "ID;Дата создания" in res_csv.content.decode("utf-8-sig", errors="replace"))

        res_bad_header = client.put(
            "/api/v1/admin/content/header",
            headers=auth_hdr,
            json={"data": {
                "phone": "+7 (423) 2222222222222222222222",
                "phone_clean": "+74232000000222222222222222",
                "working_hours": "9:00-21:00",
                "tg_link": "https://t.me/",
                "wa_link": "https://wa.me/74232000000",
                "cta_button": "ОСТАВИТЬ ЗАЯВКУ"
            }}
        )
        record("Серверная валидация отклоняет битый телефон в админке (HTTP 422)", res_bad_header.status_code == 422)

        res_media = client.get("/api/v1/admin/upload", headers=auth_hdr)
        record("GET /api/v1/admin/upload отдает список медиа на сервере (HTTP 200)", res_media.status_code == 200 and "files" in res_media.json())

        res_hdr_check = client.get("/api/v1/content")
        live_header_phone = res_hdr_check.json().get("sections", {}).get("header", {}).get("phone", "")
        record("Боевая секция header содержит валидный номер телефона", live_header_phone == "+7 (423) 200-00-00", f"Got: {live_header_phone}")

    print("\n============================================================")
    print(f"ИТОГИ БОЕВОЙ ПРОВЕРКИ: {passed}/{total} тестов пройдено ({passed/total*100:.1f}%)")
    print("============================================================")
    return passed == total

if __name__ == "__main__":
    success = run_live_tests()
    exit(0 if success else 1)
