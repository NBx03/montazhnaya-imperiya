# Архитектура проекта

Документ описывает устройство системы «Монтажная Империя» целиком: фронтенд, бэкенд, базу данных, админ-панель и типовые сценарии доработки. Предназначен для разработчиков и агентских инструментов.

---

## 1. Общая схема работы

В продакшне весь трафик принимает **Caddy 2** (`Caddyfile.production`):

- Статический лендинг (`dist/`: `index.html`, `privacy.html`, `404.html`, `/assets/*`, `/images/*`, `/videos/*`, `/icons/*`) отдаётся напрямую с диска.
- Запросы `/api/*`, `/admin*`, `/uploads/*`, `/docs*`, `/redoc*`, `/openapi.json` проксируются на локальный процесс FastAPI (`127.0.0.1:8000`).
- `/assets/*` отдаются с `Cache-Control: public, max-age=31536000, immutable`; HTML-страницы и `/admin*` — с `Cache-Control: no-cache`, чтобы правки в админке и обновления SPA подхватывались сразу.

Поток данных при открытии главной страницы:

1. Браузер получает предрендеренный `index.html`.
2. `src/main.js` запускает модули интерфейса и `initContentLoader()`.
3. `content-loader.js` проверяет кэш в `sessionStorage` (`montazh_content_cache` + `montazh_content_etag`) и отправляет `GET /api/v1/content` с заголовком `If-None-Match`.
4. При ответе `200` новые данные из БД применяются к DOM (с санитизацией URL и медиа-путей); при `304 Not Modified` используется кэш; при ошибке сети страница остаётся рабочей на статической разметке.

---

## 2. Frontend (`src/`, `index.html`)

Сборка — Vite 5 (`vite.config.js`), 3 entrypoints (`index.html`, `404.html`, `privacy.html`).

### 2.1. Модули (`src/js/modules/`)

| Файл | Экспорты | Назначение |
| :--- | :--- | :--- |
| `content-loader.js` | `initContentLoader()` | Загрузка 11 секций из `/api/v1/content` (ETag/304), гидрация текстов, контактов, изображений и Hero-видео, XSS-фильтрация ссылок. |
| `header.js` | `initHeader()`, `openMobileMenu()`, `closeMobileMenu()` | Скрытие шапки при скролле вниз (`>80px`), показ при скролле вверх, управление мобильным меню `#mobile-drawer`. |
| `hero.js` | `initHero()` | Автоплей `<video id="hero-bg-video">`, тикающий таймер `#rec-timer`, текущая дата в `#hero-date`. |
| `scroll-reveal.js` | `initScrollReveals()` | `IntersectionObserver` для секций `#expertise`, `#services`, `#steps` (добавляет `.is-visible`). |
| `odometer.js` | `animateOdometerGroup()`, `initOdometers()` | Анимация счётчиков статистики (`1 - (1 - p)^4`) в `#why-us` и при переключении кейсов. |
| `stages.js` | `initStages()` | Перспективный наклон 3D-иллюстрации `#installation-3d-wrap` за курсором и взаимоисключающая подсветка шагов `01–05`. |
| `sectors.js` | `initSectors()` | Горизонтальный скролл карточек `#sectors-track` и бегущая строка логотипов `#bank-ticker-track` (ускорение от скролла, пауза на hover). |
| `cases.js` | `initCases()` | Стопка карточек `#cases` (`card-pos-front`, `card-pos-middle`, `card-pos-back`), переключение табов и перезапуск одометра. |
| `faq.js` | `initFaq()` | Аккордеон `.faq-row` через CSS Grid (`grid-template-rows: 0fr -> 1fr`). |
| `phone-mask.js` | `initPhoneMasks()`, `cleanPhoneDigits()`, `isPhoneValid()` | Маска `+7 (XXX) XXX-XX-XX` для `input[type="tel"]`, нормализация `8`/`9`, валидация 11 цифр. |
| `modals.js` | `initModals()`, `openLeadModal()`, `closeLeadModal()`, `openSuccessModal()`, `closeSuccessModal()` | Модалка заявки и окно подтверждения, отправка `POST /api/v1/leads` (включая honeypot-поле `company_website`). |

### 2.2. Карта секций лендинга и ключей в БД

Каждая секция в `index.html` соответствует записи `section_key` в таблице `site_content` (задаются в `backend/app/seed.py`):

| `order` | `section_key` | Селектор в DOM | Что хранится в `data` |
| :---: | :--- | :--- | :--- |
| `1` | `header` | `#header`, `#mobile-drawer` | `phone`, `phone_clean`, `working_hours`, `tg_link`, `wa_link`, `cta_button`, `logo_image` |
| `2` | `hero` | `#hero` | `title`, `description`, `features[]`, `subtext`, `cta_button`, `bg_video`, `bg_poster` |
| `3` | `expertise` | `#expertise` | `title`, `lead`, `items[]` (`title`, `desc`, `image`) |
| `4` | `services` | `#services` | `title`, `subtitle`, `banner_image`, `items[]` (`name`, `desc`, `image`) |
| `5` | `why_us` | `#why-us` | `items[]` (`val`, `unit`, `title`, `desc`), `ticker_photos` (`worker_yellow`, `cables`, `worker_helmet`) |
| `6` | `steps` | `#steps` | `title`, `illustration_image`, `items[]` (`step`, `name`, `desc`) |
| `7` | `sectors` | `#sectors` | `title`, `items[]` (`title`, `desc`, `image`, `icon`), `partner_logos[]` |
| `8` | `cases` | `#cases` | `title`, `items[]` (`title`, `scope`, `image`) |
| `9` | `engineer_cta` | `#consult-form`, `#lead-modal`, `#success-modal` | `title`, `subtitle`, `button_text`, `engineer_photo`, `success_bg_image` |
| `10` | `faq` | `#faq` | `title`, `items[]` (`q`, `a`) |
| `11` | `contacts` | `#footer` | `title`, `phone`, `phone_clean`, `email`, `address`, `hours`, `inn`, `tg_link`, `wa_link`, `footer_logo` |

### 2.3. Стили и токены (`src/style.css`, `tailwind.config.js`)

- **Палитра:** `#0E1014` (`brand-dark`), `#14171D` (`brand-surface`), `#E02D37` (`brand-red`), `#FF4D55`.
- **Шрифты:** `Onest` (`font-sans`), `Fira Sans Extra Condensed` / `Sofia Sans Condensed` (`font-condensed`), `JetBrains Mono` (`font-mono`).
- **Декоративные классы:** `.cut-corner-badge`, `.tech-btn-chamfer`, `.bg-tech-grid`, `.plate-sec2`, `.plate-sec5`, `.plate-sec6`.

---

## 3. Backend (`backend/app/`)

Точка входа: `backend/app/main.py`. Конфигурация загружается из `.env` через `pydantic-settings` (`backend/app/config.py`).

### 3.1. База данных (`models.py`, `database.py`)

Используется SQLite в режиме `WAL` с `PRAGMA foreign_keys = ON` и `busy_timeout = 30000`. Таблицы:

- `admin_users` — логин (`username`), `bcrypt`-хеш пароля (`hashed_password`), `created_at`.
- `site_content` — `section_key` (unique), `title`, `order`, JSON-поле `data`, `updated_at`.
- `leads` — `name`, `phone`, `source`, `status` (`new` / `processed`), `notes`, `created_at`.
- `media_assets` — реестр загруженных файлов: `filename` (unique UUID-имя на диске), `url`, `original_name`, `content_type`, `size_bytes`, `section_key`, `field_path`, `last_used_at`, `created_at`.

### 3.2. Валидация и роутеры

- **`routers/auth.py`**: `POST /api/v1/auth/login` (rate limit `5/10min`, выпуск HS256 JWT на 7 дней), `GET /api/v1/auth/me`.
- **`routers/content.py`**:
  - `GET /api/v1/content` — отдаёт все 11 секций + слабый `ETag` и `304 Not Modified`.
  - `PUT /api/v1/admin/content/{section_key}` — прогоняет payload через `validate_section_payload` из `schemas.py` (строгие лимиты длин, проверка телефона `10–15` цифр, запрет `<script`, `javascript:`, `data:`, `..`), сохраняет секцию и обновляет привязки `section_key` / `field_path` / `last_used_at` в `media_assets`.
- **`routers/leads.py`**:
  - `POST /api/v1/leads` — rate limit `5/min`, если заполнено honeypot-поле `company_website` или `website`, тихо возвращает `200` без записи в БД.
  - `GET /api/v1/admin/leads`, `PATCH /api/v1/admin/leads/{id}`, `DELETE /api/v1/admin/leads/{id}`, `GET /api/v1/admin/leads/export-csv` (UTF-8 BOM, экранирование формул `=`, `+`, `-`, `@` апострофом от CSV injection).
- **`routers/upload.py`**:
  - `POST /api/v1/admin/upload` — принимает файл до 25 МБ + опциональные поля `section_key` и `field_path`. Проверяет magic bytes (MP4 `ftyp`, WebM `1A 45 DF A3`, реальное декодирование картинок через Pillow), конвертирует изображения в WebP (`quality=85`), сохраняет в `backend/uploads/` и создаёт запись в `media_assets`.
  - `GET /api/v1/admin/upload` — объединяет файлы на диске с метаданными из `media_assets` и помечает `is_active`, сверяя ссылки с текущим `site_content`.
  - `DELETE /api/v1/admin/upload/{filename}` — защита от path traversal, удаляет файл и запись из `media_assets`.

### 3.3. Ограничение размера тела запроса (`main.py`)

Middleware `limit_request_payload_size` отсекает запросы до чтения тела с кодом `413`:
- Для `/api/v1/admin/upload*` лимит `MAX_UPLOAD_SIZE_BYTES + 1 МБ` (по умолчанию ~26 МБ).
- Для остальных эндпоинтов (формы, JSON, логин) — `1 МБ`.

---

## 4. Админ-панель (`backend/static_admin/`)

SPA-интерфейс без сборки (`index.html`, `login.html`, `admin.css`, `admin.js`).

Вкладки разделены по принципу **одна задача — одна вкладка**:

1. **`📋 Входящие заявки` (`#tab-leads`)** — счётчики, фильтр по статусу, поиск, редактирование заметок (`#notes-modal`), смена статуса, кнопка быстрого перехода в WhatsApp, удаление, экспорт CSV.
2. **`✍️ Тексты и контакты` (`#tab-content`)** — редактирование исключительно текстов, цифр, телефонов и ссылок по 11 секциям. Медиа-поля (`isMediaFieldKey`) намеренно не рендерятся в этой форме, но автоматически сохраняются внутри JSON при отправке `PUT /api/v1/admin/content/{section_key}`. Есть автосинхронизация `phone` -> `phone_clean`, инлайн-валидация и шорткат `Ctrl/Cmd + S`.
3. **`🖼️ Медиа сайта` (`#tab-media`)** — единая визуальная карта всех 37 медиа-слотов лендинга (`getSiteMediaSlots()`), сгруппированных по блокам. Загрузка по клику или Drag & Drop сразу заливает файл с тегами слота и обновляет секцию без отдельного нажатия «Сохранить». При наличии прошлых версий на карточке появляется кнопка `🕘 N` (быстрый выбор в `#slot-history-modal`); изменённые слоты можно сбросить к исходному ассету (`↺ Сбросить`).
4. **`🕘 История медиа` (`#tab-media-history`)** — список всех загруженных файлов с фильтром («Все файлы» / «Можно вернуть» / «Сейчас на сайте»), бейджем привязанного слота, исходным именем, кнопкой мгновенного отката `⚡ Вернуть на сайт`, копированием URL и удалением (с предупреждением, если файл активен на сайте).

---

## 5. Типовые задачи (Playbook)

### Добавить или изменить текстовое поле в существующей секции

1. Обновите дефолт в `backend/app/seed.py` (`DEFAULT_SECTIONS`).
2. Добавьте поле и ограничения в соответствующую Pydantic-модель в `backend/app/schemas.py`.
3. Добавьте подпись поля и лимит в `FIELD_LIMITS` / `humanizeKey()` в `backend/static_admin/admin.js` (если ключ новый).
4. Привяжите DOM-элемент в `src/js/modules/content-loader.js` и в `index.html`.
5. Прогоните `python backend/manage.py seed` (или обновите секцию в БД) и тесты `backend/test_stage2.py`, `backend/test_stage4_deep.py`.

### Добавить новый медиа-слот на сайт

1. Убедитесь, что имя ключа в `seed.py` и `schemas.py` подпадает под `isMediaFieldKey(key)` в `backend/static_admin/admin.js` (содержит `image`, `photo`, `logo`, `icon`, `poster`, `video`), чтобы слот не дублировался в текстовом редакторе.
2. Зарегистрируйте слот в `getSiteMediaSlots()` в `backend/static_admin/admin.js` (`group`, `badge`, `title`, `sectionKey`, `path`, `defaultSrc`, `kind`).
3. Добавьте гидрацию этого элемента в `src/js/modules/content-loader.js` (через `setImageSrc` или видео-источник) и соберите фронтенд (`npm run build`).

### Перезапустить сервис и обновить продакшн

Подробные команды настройки окружения, systemd-юнитов, резервного копирования и деплоя собраны в [backend/README.md](./backend/README.md).
