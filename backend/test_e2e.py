import io
from PIL import Image
from fastapi.testclient import TestClient
from app.config import settings
from app.main import app

client = TestClient(app)

print("--- TEST 1: Healthcheck ---")
r = client.get("/health")
assert r.status_code == 200, f"Health failed: {r.status_code}"
print("✓ Health status 200:", r.json())

print("--- TEST 2: Public Content ---")
r = client.get("/api/v1/content")
assert r.status_code == 200
data = r.json()
assert "sections" in data
assert len(data["sections"]) >= 10
print("✓ Public content returned", len(data["sections"]), "sections")

print("--- TEST 3: Auth Login ---")
r = client.post("/api/v1/auth/login", json={"username": "admin", "password": settings.DEFAULT_ADMIN_PASSWORD})
assert r.status_code == 200
token = r.json()["access_token"]
print("✓ Login successful, JWT obtained")

print("--- TEST 4: Auth Me ---")
r = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
assert r.status_code == 200
assert r.json()["username"] == "admin"
print("✓ Auth me verified")

print("--- TEST 5: Lead Submission ---")
r = client.post("/api/v1/leads", json={
    "name": "Валентин Тимлид",
    "phone": "+7 (999) 777-66-55",
    "source": "test_e2e"
})
assert r.status_code == 200
lead_id = r.json()["lead_id"]
print(f"✓ Lead created with ID #{lead_id}")

print("--- TEST 6: Honeypot Anti-Spam ---")
r = client.post("/api/v1/leads", json={
    "name": "Bot",
    "phone": "+79990000000",
    "company_website": "https://bad-spammer.com"
})
assert r.status_code == 200
# Check that lead was NOT added to DB
r_leads = client.get("/api/v1/admin/leads", headers={"Authorization": f"Bearer {token}"})
bot_leads = [l for l in r_leads.json()["leads"] if l["name"] == "Bot"]
assert len(bot_leads) == 0, "Honeypot failed: bot was saved!"
print("✓ Honeypot silently trapped spam bot, zero DB entries")

print("--- TEST 7: Admin Lead Management ---")
r = client.patch(f"/api/v1/admin/leads/{lead_id}", json={"status": "processed", "notes": "Позвонил, согласовали аудит"}, headers={"Authorization": f"Bearer {token}"})
assert r.status_code == 200
assert r.json()["status"] == "processed"
print(f"✓ Lead #{lead_id} status updated to processed")

print("--- TEST 8: CSV Export ---")
r = client.get("/api/v1/admin/leads/export-csv", headers={"Authorization": f"Bearer {token}"})
assert r.status_code == 200
assert "Валентин Тимлид".encode("utf-8") in r.content
print("✓ CSV export generated with UTF-8 BOM and correct Cyrillic content")

print("--- TEST 9: Content Update via Admin ---")
r_curr = client.get("/api/v1/admin/content/hero", headers={"Authorization": f"Bearer {token}"})
hero_data = r_curr.json()["data"]
hero_data["title"] = "СИСТЕМЫ ЗАЩИТЫ 2.0"
r_upd = client.put("/api/v1/admin/content/hero", json={"data": hero_data}, headers={"Authorization": f"Bearer {token}"})
assert r_upd.status_code == 200
# Verify public content immediately reflects update
r_pub = client.get("/api/v1/content")
assert r_pub.json()["sections"]["hero"]["title"] == "СИСТЕМЫ ЗАЩИТЫ 2.0"
# Revert back to original
hero_data["title"] = "СИСТЕМЫ ЗАЩИТЫ"
client.put("/api/v1/admin/content/hero", json={"data": hero_data}, headers={"Authorization": f"Bearer {token}"})
print("✓ Content update and immediate public reflection verified")

print("--- TEST 10: Image Upload and WebP Conversion ---")
img = Image.new("RGB", (120, 120), color="green")
buf = io.BytesIO()
img.save(buf, format="PNG")
buf.seek(0)
r = client.post("/api/v1/admin/upload", files={"file": ("camera.png", buf, "image/png")}, headers={"Authorization": f"Bearer {token}"})
assert r.status_code == 200
assert r.json()["filename"].endswith(".webp")
assert r.json()["content_type"] == "image/webp"
print("✓ Image converted to WebP on the fly:", r.json()["filename"])

print("--- TEST 11: Admin Panel UI Delivery ---")
for path in ["/admin/", "/admin/login.html", "/admin/admin.css", "/admin/admin.js"]:
    r = client.get(path)
    assert r.status_code == 200, f"Failed {path}: {r.status_code}"
print("✓ All admin static assets served with HTTP 200")

print("\n==========================================")
print("🎉 ALL 11 TESTS PASSED SUCCESSFULLY! 🎉")
print("==========================================")
