# Backend & Ops — «Монтажная Империя»

Бэкенд-приложение на FastAPI, CLI-утилиты, SPA-админка и конфиги деплоя.

---

## Окружение и конфигурация

Конфигурация читается из `backend/.env` через `app/config.py`. Шаблон — `backend/.env.example`.

Основные переменные:
- `ENVIRONMENT` — `development` или `production`.
- `DATABASE_URL` — по умолчанию `sqlite+aiosqlite:///./database.sqlite` (относительные пути автоматически разворачиваются относительно `backend/`).
- `SECRET_KEY` — ключ подписи JWT (HS256, срок жизни токена — 7 дней). **В продакшне обязательно менять на длинную случайную строку.**
- `CORS_ORIGINS` — JSON-список разрешённых origin (`http://localhost:5173`, `https://montazh.documentics.ru` и т.д.).
- `DEFAULT_ADMIN_USERNAME` / `DEFAULT_ADMIN_PASSWORD` — учётка, которая создаётся при первичном `manage.py seed`.
- `ENABLE_DOCS` — `true`/`false` для включения `/docs`, `/redoc`, `/openapi.json`.

---

## Управление через `manage.py`

Все команды запускаются из папки `backend/`:

```bash
python manage.py status                          # Проверить подключение к БД, режим WAL и счётчики записей
python manage.py seed                            # Создать таблицы и заполнить 11 секций (если их нет) + админа
python manage.py create-admin -u admin -p PASS   # Создать нового админа или сменить пароль существующему
python manage.py export-content                  # Выгрузить текущие секции в backend/content_dump.json
python manage.py reset-db                        # Полностью пересоздать таблицы и заново пролить сиды (с подтверждением)
```

При старте FastAPI через `uvicorn` функция `lifespan` автоматически вызывает `settings.ensure_directories()` и `init_db()` (создание недостающих таблиц/индексов и включение `WAL`).

---

## REST API (краткий справочник)

| Метод | Путь | Доступ | Назначение |
| :--- | :--- | :--- | :--- |
| `GET` | `/health`, `/api/v1/health` | Публичный | Статус сервиса (`ok`, окружение) |
| `GET` | `/api/v1/content` | Публичный | Все 11 секций сайта + `ETag` (`304 Not Modified`) |
| `POST` | `/api/v1/leads` | Публичный (`5/min`) | Приём заявок с лендинга + honeypot-ловушка для ботов |
| `POST` | `/api/v1/auth/login` | Публичный (`5/10min`) | Выдача Bearer JWT токена |
| `GET` | `/api/v1/auth/me` | Bearer JWT | Данные текущего администратора |
| `GET` | `/api/v1/admin/content` | Bearer JWT | Список всех секций для админки |
| `PUT` | `/api/v1/admin/content/{section_key}` | Bearer JWT | Валидация (`schemas.py`), сохранение секции и привязок `MediaAsset` |
| `POST` | `/api/v1/admin/upload` | Bearer JWT | Загрузка фото (конвертация в WebP) или видео MP4/WebM до 25 МБ (`section_key`, `field_path`) |
| `GET` | `/api/v1/admin/upload` | Bearer JWT | Список файлов в `uploads/` + метаданные слотов и флаг `is_active` |
| `DELETE` | `/api/v1/admin/upload/{filename}` | Bearer JWT | Удаление файла с диска и записи из `media_assets` |
| `GET` | `/api/v1/admin/leads` | Bearer JWT | Список заявок со счётчиками `total`, `new_count`, `processed_count` |
| `PATCH` | `/api/v1/admin/leads/{lead_id}` | Bearer JWT | Обновление статуса (`new` / `processed`) и заметок менеджера |
| `DELETE` | `/api/v1/admin/leads/{lead_id}` | Bearer JWT | Удаление заявки |
| `GET` | `/api/v1/admin/leads/export-csv` | Bearer JWT | Экспорт всех заявок в CSV (UTF-8 BOM, защита от формул) |

---

## Тестирование

Локальные наборы запускаются из **корня проекта** (важно, так как `test_stage4_deep.py` читает `index.html` и `dist/`):

```bash
python backend/manage.py seed
python backend/test_stage2.py       # API, ETag 304, brute-force лимитер, CSV injection, загрузка медиа, валидация
python backend/test_stage3.py       # Статика админки, auth-барьер, структура редактора
python backend/test_stage4.py       # Интеграция лендинга, honeypot, rate-limit заявок
python backend/test_stage4_deep.py  # Сверка DOM-селекторов index.html со схемой API
python backend/test_stage5.py       # Проверки systemd, backup.sh, Caddyfile.production, privacy.html
python backend/test_e2e.py          # Сквозной сценарий основных пользовательских путей
```

Проверка живого сервера (`https://montazh.documentics.ru` или URL из `LIVE_URL`):

```bash
LIVE_URL=https://montazh.documentics.ru LIVE_ADMIN_USERNAME=admin LIVE_ADMIN_PASSWORD=... python backend/test_live_production.py
```

---

## Продакшн-деплой и обслуживание

Серверная раскладка, на которую настроены юниты в репозитории:
- Статика фронтенда (`dist/`): `/var/www/montazh`
- Бэкенд и админка: `/var/www/montazh-backend`
- Прокси-сервер: `/etc/caddy/Caddyfile` (конфиг блока сайта в корне — `Caddyfile.production`)

### Первичная установка systemd-юнитов (на сервере)

```bash
cp /var/www/montazh-backend/montazh-backend.service /etc/systemd/system/
cp /var/www/montazh-backend/montazh-backup.service /etc/systemd/system/
cp /var/www/montazh-backend/montazh-backup.timer /etc/systemd/system/
chmod +x /var/www/montazh-backend/backup.sh

systemctl daemon-reload
systemctl enable --now montazh-backend
systemctl enable --now montazh-backup.timer
```

> Важно: в `montazh-backend.service` специально стоит `--workers 1`, так как `slowapi` хранит счётчики rate-limit в памяти процесса.

### Резервное копирование

`backup.sh` использует нативный `sqlite3 .backup` (безопасно при активном WAL), проверяет целостность через `PRAGMA quick_check`, сжимает снапшот через `gzip` в `backend/backups/` и удаляет архивы старше 14 дней. По таймеру `montazh-backup.timer` скрипт запускается автоматически.

### Типовое обновление

- При правках в `backend/app/` или `backend/static_admin/`: скопировать файлы на сервер в `/var/www/montazh-backend` и выполнить `systemctl restart montazh-backend`.
- При правках фронтенда: выполнить `npm run build` и синхронизировать содержимое `dist/` в `/var/www/montazh`.
