"""
Stage 2 REST API Comprehensive Test Suite.

Verifies:
1. Public content ETag & 304 Not Modified caching.
2. Brute-force protection on /api/v1/auth/login.
3. Proxy-aware real client IP resolution (X-Forwarded-For).
4. CSV Formula Injection (CWE-1236) sanitization.
5. Upload security: magic bytes check (spoofed MP4 rejection) and WebP optimization.
6. Localized 429 Too Many Requests JSON responses.
"""

import copy
import io
from fastapi.testclient import TestClient
from PIL import Image
from app.config import settings
from app.main import app

client = TestClient(app)

print("=" * 60)
print("  ЭТАП 2: КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ REST API")
print("=" * 60)

# TEST 1: Healthcheck
print("\n[TEST 1] Проверка эндпоинта /health...")
r = client.get("/health")
assert r.status_code == 200
assert r.json()["status"] == "ok"
print("  ✓ Healthcheck успешен (HTTP 200)")

# TEST 2: Public Content with ETag & 304 Not Modified
print("\n[TEST 2] Проверка ETag и кеширования (304 Not Modified)...")
r1 = client.get("/api/v1/content")
assert r1.status_code == 200
etag = r1.headers.get("etag")
cache_control = r1.headers.get("cache-control")
assert etag is not None, "ETag header missing!"
assert "public" in cache_control, "Cache-Control header missing!"

# Conditional GET with matching If-None-Match
r2 = client.get("/api/v1/content", headers={"If-None-Match": etag})
assert r2.status_code == 304, f"Expected 304 Not Modified, got {r2.status_code}"
print(f"  ✓ Первый запрос: HTTP 200 + ETag: {etag}")
print("  ✓ Повторный условный запрос: HTTP 304 Not Modified (БД не нагружается)")

# TEST 3: Auth Login & JWT
print("\n[TEST 3] Авторизация администратора...")
r = client.post("/api/v1/auth/login", json={"username": "admin", "password": settings.DEFAULT_ADMIN_PASSWORD})
assert r.status_code == 200
token = r.json()["access_token"]
print("  ✓ Успешный вход, получен валидный JWT токен")

# TEST 4: Brute-Force Rate Limiting on Login
print("\n[TEST 4] Проверка защиты от подбора паролей (Brute-force)...")
# Send requests from a specific simulated attacker IP
attacker_headers = {"X-Forwarded-For": "198.51.100.42"}
for i in range(1, 6):
    r_fail = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "WrongPassword!"},
        headers=attacker_headers
    )
    assert r_fail.status_code == 401, f"Attempt {i} expected 401, got {r_fail.status_code}"

# 6th attempt should be blocked with 429
r_blocked = client.post(
    "/api/v1/auth/login",
    json={"username": "admin", "password": "WrongPassword!"},
    headers=attacker_headers
)
assert r_blocked.status_code == 429, f"Expected 429 Too Many Requests, got {r_blocked.status_code}"
err_data = r_blocked.json()
assert err_data["code"] == "RATE_LIMIT_EXCEEDED"
print(f"  ✓ 5 неверных попыток вернули HTTP 401")
print(f"  ✓ 6-я попытка заблокирована: HTTP 429 ({err_data['message']})")

# TEST 5: CSV Formula Injection (CWE-1236) Protection
print("\n[TEST 5] Защита от CSV Formula Injection...")
# Submit a lead with dangerous formula payload in name
r_inj = client.post("/api/v1/leads", json={
    "name": "=cmd|' /C calc'!A0",
    "phone": "+7 (999) 555-44-33",
    "source": "formula_test"
})
assert r_inj.status_code == 200
lead_id = r_inj.json()["lead_id"]

# Export CSV
r_csv = client.get("/api/v1/admin/leads/export-csv", headers={"Authorization": f"Bearer {token}"})
assert r_csv.status_code == 200
csv_text = r_csv.content.decode("utf-8-sig")

# Verify that formula is escaped with single quote: "'=cmd|' /C calc'!A0"
assert "'=cmd|' /C calc'!A0" in csv_text, "Dangerous formula was NOT escaped with single quote!"
print("  ✓ Опасная формула '=cmd|...' автоматически обезврежена апострофом в CSV")

# Cleanup injected lead
client.delete(f"/api/v1/admin/leads/{lead_id}", headers={"Authorization": f"Bearer {token}"})

# TEST 6: Upload Validation - Spoofed File Type Rejection
print("\n[TEST 6] Защита от загрузки поддельных файлов (Magic Bytes)...")
# Send fake MP4 (text file pretending to be video/mp4)
fake_mp4 = b"This is just a dangerous shell script disguised as video"
r_fake = client.post(
    "/api/v1/admin/upload",
    files={"file": ("exploit.mp4", io.BytesIO(fake_mp4), "video/mp4")},
    headers={"Authorization": f"Bearer {token}"}
)
assert r_fake.status_code == 400, f"Expected 400 Bad Request for fake MP4, got {r_fake.status_code}"
print("  ✓ Поддельное видео без сигнатуры ftyp заблокировано (HTTP 400)")

# Valid MP4 & WebM header checks
valid_mp4_header = b"\x00\x00\x00\x20ftypmp42\x00\x00\x00\x00mp42isom"
r_valid_mp4 = client.post(
    "/api/v1/admin/upload",
    files={"file": ("sample.mp4", io.BytesIO(valid_mp4_header), "video/mp4")},
    headers={"Authorization": f"Bearer {token}"}
)
assert r_valid_mp4.status_code == 200
mp4_filename = r_valid_mp4.json()["filename"]

valid_webm_header = b"\x1a\x45\xdf\xa3\x9f\x42\x86\x81\x01"
r_valid_webm = client.post(
    "/api/v1/admin/upload",
    files={"file": ("loop.webm", io.BytesIO(valid_webm_header), "video/webm")},
    headers={"Authorization": f"Bearer {token}"}
)
assert r_valid_webm.status_code == 200
webm_filename = r_valid_webm.json()["filename"]
print(f"  ✓ Валидные MP4 и WebM файлы приняты: {mp4_filename}, {webm_filename}")

# TEST 7: Image Optimization & WebP Conversion + Media History Metadata & Cleanup
print("\n[TEST 7] Конвертация изображений в WebP, история привязок и удаление медиа...")
img = Image.new("RGB", (300, 200), color="crimson")
buf = io.BytesIO()
img.save(buf, format="PNG")
buf.seek(0)

r_img = client.post(
    "/api/v1/admin/upload",
    files={"file": ("banner_history.png", buf, "image/png")},
    data={"section_key": "services", "field_path": "items.0.image"},
    headers={"Authorization": f"Bearer {token}"}
)
assert r_img.status_code == 200
data_img = r_img.json()
assert data_img["filename"].endswith(".webp")
assert data_img["content_type"] == "image/webp"
assert data_img["original_name"] == "banner_history.png"

# Before assigning to content, file should appear in list with is_active=False and slot metadata
r_media_list = client.get("/api/v1/admin/upload", headers={"Authorization": f"Bearer {token}"})
assert r_media_list.status_code == 200
files_map = {f["filename"]: f for f in r_media_list.json()["files"]}
assert data_img["filename"] in files_map and mp4_filename in files_map
assert files_map[data_img["filename"]]["original_name"] == "banner_history.png"
assert files_map[data_img["filename"]]["section_key"] == "services"
assert files_map[data_img["filename"]]["field_path"] == "items.0.image"
assert files_map[data_img["filename"]]["is_active"] is False

# Assign uploaded URL into services.items[0].image and verify is_active becomes True
orig_services = client.get("/api/v1/content").json()["sections"]["services"]
patched_services = copy.deepcopy(orig_services)
patched_services["items"][0]["image"] = data_img["url"]
r_patch = client.put(
    "/api/v1/admin/content/services",
    json={"data": patched_services},
    headers={"Authorization": f"Bearer {token}"}
)
assert r_patch.status_code == 200

files_after_assign = {f["filename"]: f for f in client.get("/api/v1/admin/upload", headers={"Authorization": f"Bearer {token}"}).json()["files"]}
assert files_after_assign[data_img["filename"]]["is_active"] is True

# Restore original services section -> is_active drops back to False
r_restore = client.put(
    "/api/v1/admin/content/services",
    json={"data": orig_services},
    headers={"Authorization": f"Bearer {token}"}
)
assert r_restore.status_code == 200
files_after_restore = {f["filename"]: f for f in client.get("/api/v1/admin/upload", headers={"Authorization": f"Bearer {token}"}).json()["files"]}
assert files_after_restore[data_img["filename"]]["is_active"] is False

# Verify path traversal rejection on DELETE & clean up test media files
assert client.delete("/api/v1/admin/upload/../../.env", headers={"Authorization": f"Bearer {token}"}).status_code in (400, 404)
assert client.delete(f"/api/v1/admin/upload/{data_img['filename']}", headers={"Authorization": f"Bearer {token}"}).status_code == 200
assert client.delete(f"/api/v1/admin/upload/{mp4_filename}", headers={"Authorization": f"Bearer {token}"}).status_code == 200
assert client.delete(f"/api/v1/admin/upload/{webm_filename}", headers={"Authorization": f"Bearer {token}"}).status_code == 200
print(f"  ✓ Изображение PNG пережато в WebP: {data_img['filename']}, история привязок и безопасное удаление проверены")

# TEST 8: Content Validation (Reject empty data & malformed phones/emails/urls)
print("\n[TEST 8] Валидация входных данных секций...")
r_empty = client.put(
    "/api/v1/admin/content/hero",
    json={"data": {}},
    headers={"Authorization": f"Bearer {token}"}
)
assert r_empty.status_code == 422, f"Expected 422 Unprocessable Entity, got {r_empty.status_code}"

# Oversized invalid phone in header
r_bad_phone = client.put(
    "/api/v1/admin/content/header",
    json={"data": {
        "phone": "+7 (423) 2222222222222222222222",
        "phone_clean": "+742320000002222222222222222222",
        "working_hours": "9:00-21:00",
        "tg_link": "https://t.me/",
        "wa_link": "https://wa.me/74232000000",
        "cta_button": "ЗАЯВКА"
    }},
    headers={"Authorization": f"Bearer {token}"}
)
assert r_bad_phone.status_code == 422, f"Oversized phone must return 422, got {r_bad_phone.status_code}"

# Dangerous javascript: link in header
r_bad_url = client.put(
    "/api/v1/admin/content/header",
    json={"data": {
        "phone": "+7 (423) 200-00-00",
        "phone_clean": "+74232000000",
        "working_hours": "9:00-21:00",
        "tg_link": "javascript:alert(1)",
        "wa_link": "https://wa.me/74232000000",
        "cta_button": "ЗАЯВКА"
    }},
    headers={"Authorization": f"Bearer {token}"}
)
assert r_bad_url.status_code == 422, f"Unsafe URI must return 422, got {r_bad_url.status_code}"

print("  ✓ Пустые данные, сверхдлинные телефоны и небезопасные ссылки отклонены валидатором (HTTP 422)")

print("\n" + "=" * 60)
print("  🎉 ВСЕ ТЕСТЫ ЭТАПА 2 УСПЕШНО ПРОЙДЕНЫ! 🎉")
print("=" * 60)
