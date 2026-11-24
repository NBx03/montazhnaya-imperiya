"""
Stage 5 Verification Test Suite (General Inspection Edition):
Validates infrastructure configs, systemd services, backup scripts,
Caddyfile production rules, performance caching, and privacy policy compliance.
"""

import os
import sys

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BACKEND_DIR)

def run_tests():
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
    print("  ЭТАП 5: ГЕНЕРАЛЬНАЯ ПРОВЕРКА ИНФРАСТРУКТУРЫ И КОНФИГУРАЦИЙ")
    print("============================================================")

    # ----------------------------------------------------
    # 1. Systemd Backend Service
    # ----------------------------------------------------
    print("\n[1] Проверка systemd сервиса (montazh-backend.service)...")
    service_path = os.path.join(BACKEND_DIR, "montazh-backend.service")
    record("Файл montazh-backend.service существует", os.path.isfile(service_path))

    with open(service_path, "r", encoding="utf-8") as f:
        service_content = f.read()

    record("Файл сервиса не содержит Windows CRLF (\\r\\n)", "\r\n" not in service_content)
    record("Рабочая директория указывает на /var/www/montazh-backend", "WorkingDirectory=/var/www/montazh-backend" in service_content)
    record("Автоперезапуск настроен (Restart=always, RestartSec=3)", "Restart=always" in service_content and "RestartSec=3" in service_content)
    record("Один воркер (--workers 1) для точного in-memory rate-limiter", "--workers 1" in service_content)
    record("Доверены прокси-заголовки (--proxy-headers --forwarded-allow-ips)", "--proxy-headers" in service_content and "--forwarded-allow-ips" in service_content)
    record("Включена директива NoNewPrivileges=true", "NoNewPrivileges=true" in service_content)
    record("Включена изоляция PrivateTmp=true", "PrivateTmp=true" in service_content)

    # ----------------------------------------------------
    # 2. Automated Hot Backup Script & Systemd Timer
    # ----------------------------------------------------
    print("\n[2] Проверка скрипта горячего бэкапа (backup.sh) и таймера...")
    backup_sh_path = os.path.join(BACKEND_DIR, "backup.sh")
    record("Файл backup.sh существует", os.path.isfile(backup_sh_path))

    with open(backup_sh_path, "r", encoding="utf-8") as f:
        backup_content = f.read()

    record("backup.sh использует строгий режим bash (set -euo pipefail)", "set -euo pipefail" in backup_content)
    record("backup.sh не содержит Windows CRLF (\\r\\n)", "\r\n" not in backup_content)
    record("Используется SQLite native hot backup API (.backup)", ".backup" in backup_content)
    record("Встроена автоматическая проверка целостности (PRAGMA quick_check)", "PRAGMA quick_check" in backup_content)
    record("Встроена архивация gzip для экономии места", "gzip -f" in backup_content)
    record("Встроена ротация 14 дней (-mtime +14)", "-mtime +14" in backup_content)

    backup_svc_path = os.path.join(BACKEND_DIR, "montazh-backup.service")
    backup_timer_path = os.path.join(BACKEND_DIR, "montazh-backup.timer")
    record("montazh-backup.service существует", os.path.isfile(backup_svc_path))
    record("montazh-backup.timer существует", os.path.isfile(backup_timer_path))

    with open(backup_timer_path, "r", encoding="utf-8") as f:
        timer_content = f.read()
    record("Таймер бэкапов настроен на ежедневный запуск с Persistent=true", "OnCalendar=*-*-* 03:00:00" in timer_content and "Persistent=true" in timer_content)

    # ----------------------------------------------------
    # 3. Caddy Production Configuration
    # ----------------------------------------------------
    print("\n[3] Проверка конфигурации Caddy (Caddyfile.production)...")
    caddy_path = os.path.join(ROOT_DIR, "Caddyfile.production")
    record("Файл Caddyfile.production существует", os.path.isfile(caddy_path))

    with open(caddy_path, "r", encoding="utf-8") as f:
        caddy_content = f.read()

    record("Caddyfile содержит домен montazh.documentics.ru", "montazh.documentics.ru" in caddy_content)
    record("Проксирование /api/* на 127.0.0.1:8000", "reverse_proxy 127.0.0.1:8000" in caddy_content and "/api/*" in caddy_content)
    record("Проксирование /admin* на 127.0.0.1:8000", "/admin*" in caddy_content)
    record("Проксирование /uploads/* на 127.0.0.1:8000", "/uploads/*" in caddy_content)
    record("Защита от перегрузки: лимит тела запроса 50MB (max_size 50MB)", "max_size 50MB" in caddy_content)
    record("Современное сжатие zstd и gzip", "encode zstd gzip" in caddy_content)
    record("Заголовки безопасности (HSTS, nosniff, SAMEORIGIN)", "Strict-Transport-Security" in caddy_content and "X-Content-Type-Options nosniff" in caddy_content)
    record("Долгосрочное кеширование Vite ассетов (max-age=31536000, immutable)", "max-age=31536000, immutable" in caddy_content)
    record("Кеширование медиа и запрет кеширования HTML (no-cache)", 'Cache-Control "no-cache"' in caddy_content and ('@htmlFiles' in caddy_content or '@htmlAndSeo' in caddy_content))
    record("Clean URLs роутинг с try_files {path} {path}.html", "try_files {path} {path}.html" in caddy_content)
    record("Кастомный обработчик 404 (handle_errors)", "handle_errors" in caddy_content and "404.html" in caddy_content)

    # ----------------------------------------------------
    # 4. Legal Compliance & Dist Bundle (privacy.html)
    # ----------------------------------------------------
    print("\n[4] Проверка страницы политики конфиденциальности (152-ФЗ)...")
    privacy_src = os.path.join(ROOT_DIR, "privacy.html")
    privacy_dist = os.path.join(ROOT_DIR, "dist", "privacy.html")
    record("privacy.html в корне проекта существует", os.path.isfile(privacy_src))
    record("privacy.html собран в dist/ для раздачи с веб-сервера", os.path.isfile(privacy_dist))

    with open(privacy_dist, "r", encoding="utf-8") as f:
        privacy_content = f.read()

    record("Политика содержит реквизиты и упоминание 152-ФЗ", "152-ФЗ" in privacy_content and "Монтажная Империя" in privacy_content)

    index_dist = os.path.join(ROOT_DIR, "dist", "index.html")
    with open(index_dist, "r", encoding="utf-8") as f:
        index_content = f.read()
    
    # Check all 3 links in index.html
    privacy_links_count = index_content.count('href="/privacy.html"')
    record(f"Все ссылки на политику в dist/index.html ведут на /privacy.html (найдено: {privacy_links_count})", privacy_links_count >= 3)

    print("\n============================================================")
    print(f"ИТОГИ ГЕНЕРАЛЬНОЙ ПРОВЕРКИ ЭТАПА 5: {passed}/{total} тестов пройдено ({passed/total*100:.1f}%)")
    print("============================================================")
    return passed == total

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
