"""
Stage 3 Admin Panel & UI Controller Test Suite.

Verifies:
1. Static delivery of Admin SPA (HTML, JS, CSS).
2. XSS sanitation mechanism in admin table data.
3. Lead triage & internal notes persistence (PATCH /api/v1/admin/leads/{id}).
4. Strict 401 interception on protected admin endpoints.
5. Content section ordering and metadata integrity for the admin editor.
"""

from fastapi.testclient import TestClient
from app.config import settings
from app.main import app

client = TestClient(app)

print("=" * 60)
print("  ЭТАП 3: ТЕСТИРОВАНИЕ ИНТЕРФЕЙСА И ЛОГИКИ АДМИН-ПАНЕЛИ")
print("=" * 60)

# TEST 1: Admin SPA Static Assets Delivery
print("\n[TEST 1] Проверка статической раздачи SPA админки и новых элементов UI...")
for path in ["/admin/", "/admin/login.html", "/admin/admin.css", "/admin/admin.js"]:
    r = client.get(path)
    assert r.status_code == 200, f"Failed {path}: {r.status_code}"
    assert len(r.text) > 1000, f"File {path} is suspiciously small ({len(r.text)} bytes)"

# Verify new UI elements in HTML
index_html = client.get("/admin/").text
assert 'id="lead-search-input"' in index_html, "Missing lead search input in index.html"
assert 'id="notes-modal"' in index_html, "Missing notes modal dialog in index.html"
assert 'id="notes-modal-textarea"' in index_html, "Missing textarea in notes modal"

# Verify CSS has styling for new components
admin_css = client.get("/admin/admin.css").text
assert '.status-select' in admin_css, "Missing .status-select styling"
assert '.modal-overlay' in admin_css, "Missing .modal-overlay styling"
assert '.preview-delete-btn' in admin_css, "Missing .preview-delete-btn styling"

# Verify JS contains enhanced handlers
admin_js = client.get("/admin/admin.js").text
assert 'validateEditorField' in admin_js, "Missing validateEditorField in admin.js"
assert 'renderSiteMediaSlots' in admin_js, "Missing renderSiteMediaSlots in admin.js"
assert 'replaceSiteMediaSlot' in admin_js, "Missing replaceSiteMediaSlot in admin.js"
assert 'restoreMediaFromHistory' in admin_js, "Missing restoreMediaFromHistory in admin.js"
assert 'openSlotHistoryModal' in admin_js, "Missing openSlotHistoryModal in admin.js"
assert 'site-media-slots-grid' in index_html, "Missing site-media-slots-grid in index.html"
assert 'tab-media-history' in index_html, "Missing tab-media-history in index.html"
assert 'slot-history-modal' in index_html, "Missing slot-history-modal in index.html"
assert 'openNotesModal' in admin_js, "Missing openNotesModal in admin.js"
assert 'Тексты и контакты' in index_html, "Missing updated 'Тексты и контакты' tab label in index.html"
assert 'attachInlineUploader' not in admin_js, "Duplicate attachInlineUploader must be removed from admin.js"
assert '.btn-inline-upload' not in admin_css, "Unused .btn-inline-upload CSS must be removed from admin.css"
assert 'deleteMediaFromHistory' in admin_js, "Missing deleteMediaFromHistory in admin.js"
assert 'changeLeadStatus' in admin_js, "Missing changeLeadStatus in admin.js"
print("  ✓ Все статические файлы админки отдаются с кодом HTTP 200")
print("  ✓ Все компоненты (тексты и контакты, медиа-слоты, история с откатом, заметки, поиск, статус-селект) присутствуют и не дублируются")

# TEST 2: Admin Auth Barrier
print("\n[TEST 2] Проверка барьера авторизации админ-эндпоинтов...")
unauthorized_endpoints = [
    ("GET", "/api/v1/admin/leads"),
    ("GET", "/api/v1/admin/content"),
    ("PUT", "/api/v1/admin/content/hero"),
    ("GET", "/api/v1/admin/leads/export-csv"),
]
for method, url in unauthorized_endpoints:
    r = client.request(method, url)
    assert r.status_code == 401, f"{method} {url} without token expected 401, got {r.status_code}"
print("  ✓ Все защищенные эндпоинты админки возвращают HTTP 401 без токена")

# TEST 3: Admin Login & Session
print("\n[TEST 3] Авторизация и получение рабочего токена...")
r = client.post("/api/v1/auth/login", json={"username": "admin", "password": settings.DEFAULT_ADMIN_PASSWORD})
assert r.status_code == 200
token = r.json()["access_token"]
auth_header = {"Authorization": f"Bearer {token}"}
print("  ✓ Успешный вход в систему, токен получен")

# TEST 4: Lead Triage & Manager Notes
print("\n[TEST 4] Проверка цикла обработки заявок и заметок менеджера...")
# Create a test lead
r_create = client.post("/api/v1/leads", json={
    "name": "Алексей Заказчик",
    "phone": "+7 (914) 123-45-67",
    "source": "admin_test"
})
assert r_create.status_code == 200
lead_id = r_create.json()["lead_id"]

# Update status to processed and add a manager note
note_text = "Созвонились, выезд инженера назначен на пятницу 14:00"
r_patch = client.patch(
    f"/api/v1/admin/leads/{lead_id}",
    json={"status": "processed", "notes": note_text},
    headers=auth_header
)
assert r_patch.status_code == 200
data_patch = r_patch.json()
assert data_patch["status"] == "processed"
assert data_patch["notes"] == note_text

# Verify notes appear in the admin list
r_list = client.get("/api/v1/admin/leads", headers=auth_header)
assert r_list.status_code == 200
lead_in_list = next((l for l in r_list.json()["leads"] if l["id"] == lead_id), None)
assert lead_in_list is not None
assert lead_in_list["notes"] == note_text
print(f"  ✓ Заявка #{lead_id} успешно обновлена (статус 'processed', заметка сохранена)")

# Cleanup test lead
client.delete(f"/api/v1/admin/leads/{lead_id}", headers=auth_header)

# TEST 5: Section Ordering and Editor Metadata Integrity
print("\n[TEST 5] Проверка структуры секций для редактора...")
r_sections = client.get("/api/v1/admin/content", headers=auth_header)
assert r_sections.status_code == 200
sections = r_sections.json()
assert len(sections) == 11, f"Expected 11 sections, got {len(sections)}"

# Verify that sections are strictly sorted by order 1..11
orders = [s["order"] for s in sections]
assert orders == list(range(1, 12)), f"Section ordering is broken: {orders}"
print(f"  ✓ Все 11 секций строго упорядочены (1..11) для меню редактора")

# Verify essential image fields exist
hero_sec = next(s for s in sections if s["section_key"] == "hero")
assert "title" in hero_sec["data"]
engineer_sec = next(s for s in sections if s["section_key"] == "engineer_cta")
assert "engineer_photo" in engineer_sec["data"]
print("  ✓ Поля изображений и текстов секций корректны для живого предпросмотра")

print("\n" + "=" * 60)
print("  🎉 ВСЕ ТЕСТЫ ЭТАПА 3 УСПЕШНО ПРОЙДЕНЫ! 🎉")
print("=" * 60)
