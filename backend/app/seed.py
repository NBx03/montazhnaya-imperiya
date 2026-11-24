"""
Database Initialization & Seeding Script.

Populates initial site content sections and default administrator.
Reflects 100% of the actual landing page content (all 7 services, 3 metrics,
5 steps, 3 portfolio cases, 5 FAQ items, contacts, and legal info).
"""

import asyncio
from datetime import datetime, timezone
from sqlalchemy import select
from app.auth import get_password_hash
from app.config import settings
from app.database import AsyncSessionLocal, Base, engine
from app.models import AdminUser, SiteContent

DEFAULT_SECTIONS = [
    {
        "order": 1,
        "section_key": "header",
        "title": "Шапка сайта (Контакты и режим)",
        "data": {
            "phone": "+7 (423) 200-00-00",
            "phone_clean": "+74232000000",
            "working_hours": "Ежедневно 9:00–21:00",
            "tg_link": "https://t.me/",
            "wa_link": "https://wa.me/74232000000",
            "cta_button": "ОСТАВИТЬ ЗАЯВКУ",
            "logo_image": "/icons/logo-header-hd.png"
        }
    },
    {
        "order": 2,
        "section_key": "hero",
        "title": "Главный экран (Hero)",
        "data": {
            "title": "СИСТЕМЫ ЗАЩИТЫ",
            "description": "Проектируем, монтируем и настраиваем системы безопасности и электрику — от квартиры до распределённой сети филиалов.",
            "features": [
                "БИЗНЕСУ И ЧАСТНЫМ КЛИЕНТАМ",
                "ОДИН ПОДРЯДЧИК НА ВЕСЬ ЦИКЛ",
                "БЕСПЛАТНЫЙ ВЫЕЗД ИНЖЕНЕРА"
            ],
            "subtext": "Установим любые системы защиты во Владивостоке под ключ: проект, оборудование, монтаж и сдача объекта",
            "cta_button": "ОСТАВИТЬ ЗАЯВКУ",
            "bg_video": "/videos/hero-bg.mp4",
            "bg_poster": "/images/hero-rack-bg.jpg"
        }
    },
    {
        "order": 3,
        "section_key": "expertise",
        "title": "Экспертиза (01 — Экспертиза)",
        "data": {
            "title": "ПОМОГАЕМ ПРИНЯТЬ РЕШЕНИЕ, КОТОРОЕ НЕ ПРИДЁТСЯ ПЕРЕДЕЛЫВАТЬ",
            "lead": "Честно показываем, что на объекте действительно нужно. Выезд инженера и смета — бесплатно.",
            "items": [
                {
                    "title": "ГАРАНТИЯ 1 ГОД НА МОНТАЖ",
                    "desc": "Плюс официальная гарантия производителя на оборудование.",
                    "image": "/images/clean-icon-shield.png"
                },
                {
                    "title": "ПРОЕКТ, СХЕМА И СМЕТА",
                    "desc": "Проектирование небольших объектов. Крупные — по проекту заказчика.",
                    "image": "/images/clean-icon-doc.png"
                },
                {
                    "title": "СВОЁ ОБОРУДОВАНИЕ НА СКЛАДЕ",
                    "desc": "Стартуем через несколько дней, а не через месяц ожидания поставки.",
                    "image": "/images/clean-icon-box.png"
                }
            ]
        }
    },
    {
        "order": 4,
        "section_key": "services",
        "title": "Услуги и цены (02 — Тарифы)",
        "data": {
            "title": "ВСЕ СИСТЕМЫ ПОД КЛЮЧ",
            "subtitle": "Один договор, одна гарантия, одна ответственность — от проекта до обслуживания.",
            "banner_image": "/images/banner-3d-hardware.png",
            "items": [
                {
                    "name": "ВИДЕОНАБЛЮДЕНИЕ",
                    "desc": "Проектирование, монтаж и настройка IP-систем. Локальный или облачный архив и доступ с телефона.",
                    "image": "/images/service-cctv.png"
                },
                {
                    "name": "СКУД",
                    "desc": "Контроль и управление доступом: карты, биометрия, домофония, интеграция с учётом.",
                    "image": "/images/service-skud.png"
                },
                {
                    "name": "ОХРАННАЯ СИГНАЛИЗАЦИЯ",
                    "desc": "Датчики движения и открытия, тревожные кнопки, настройка сценариев оповещения.",
                    "image": "/images/service-alarm.png"
                },
                {
                    "name": "ДОМОФОНЫ",
                    "desc": "Аудио — и видеодомофония для подъездов, офисов и частных домов.",
                    "image": "/images/service-intercom.png"
                },
                {
                    "name": "ПОЖАРНАЯ СИГНАЛИЗАЦИЯ",
                    "desc": "Проект, монтаж и обслуживание АПС. Сдача надзорным органам.",
                    "image": "/images/service-fire.png"
                },
                {
                    "name": "СКС",
                    "desc": "Структурированные кабельные сети, ЛВС и серверные «под ключ».",
                    "image": "/images/service-sks.png"
                },
                {
                    "name": "ЭЛЕКТРОМОНТАЖ",
                    "desc": "Силовые и слаботочные сети, щиты, прокладка трасс. Проектирование и сдача под ключ.",
                    "image": "/images/service-electro.png"
                }
            ]
        }
    },
    {
        "order": 5,
        "section_key": "why_us",
        "title": "Метрики и стандарты (03 — Почему мы)",
        "data": {
            "items": [
                {
                    "val": "12",
                    "unit": "лет",
                    "title": "НА РЫНКЕ ПРИМОРЬЯ",
                    "desc": "работаем с 2013 года"
                },
                {
                    "val": "450",
                    "unit": "+",
                    "title": "ОБЪЕКТОВ СДАНО",
                    "desc": "от квартиры до сети филиалов"
                },
                {
                    "val": "98",
                    "unit": "%",
                    "title": "ПРИЁМКА С ПЕРВОГО РАЗА",
                    "desc": "включая государственные объекты"
                }
            ],
            "ticker_photos": {
                "worker_yellow": "/images/section03-worker-yellow.png",
                "cables": "/images/section03-cables.png",
                "worker_helmet": "/images/section03-worker-helmet.png"
            }
        }
    },
    {
        "order": 6,
        "section_key": "steps",
        "title": "Этапы работы (04 — Как мы работаем)",
        "data": {
            "title": "КАК ПРОИСХОДИТ УСТАНОВКА",
            "illustration_image": "/images/section04-installation-3d.png",
            "items": [
                {
                    "step": "01",
                    "name": "ЗАЯВКА",
                    "desc": "Оставьте заявку через сайт или позвоните нам. Мы внимательно выслушаем ваши задачи."
                },
                {
                    "step": "02",
                    "name": "КОНСУЛЬТАЦИЯ И ВЫЕЗД",
                    "desc": "Бесплатно выезжаем на объект в пределах Владивостока и Приморья, осматриваем кабельные трассы."
                },
                {
                    "step": "03",
                    "name": "ПРОЕКТ",
                    "desc": "Разрабатываем схему расстановки оборудования, трассировки кабелей и фиксированную смету."
                },
                {
                    "step": "04",
                    "name": "МОНТАЖ",
                    "desc": "Выполняем монтаж строго по ГОСТ и СНиП. Аккуратная прокладка кабеля без лишней пыли."
                },
                {
                    "step": "05",
                    "name": "СДАЧА И ПОДДЕРЖКА",
                    "desc": "Тестируем все режимы, обучаем ответственных сотрудников и выдаем исполнительную документацию."
                }
            ]
        }
    },
    {
        "order": 7,
        "section_key": "sectors",
        "title": "Сферы применения (05 — Отрасли)",
        "data": {
            "title": "РАБОТАЕМ В РАЗЛИЧНЫХ СФЕРАХ",
            "items": [
                {
                    "title": "КОММЕРЧЕСКАЯ НЕДВИЖИМОСТЬ",
                    "desc": "Торговые центры, магазины и общественные пространства. Подбираем решения с учётом внешнего вида, функциональности и сроков ввода.",
                    "image": "/images/sector-commercial.png",
                    "icon": "/images/sector-icon-home.png"
                },
                {
                    "title": "СОЦИАЛЬНЫЕ И ГОСУДАРСТВЕННЫЕ ОБЪЕКТЫ",
                    "desc": "Школы, детские сады и другие учреждения. Работаем с требованиями по безопасности, энергоэффективности и нормативам эксплуатации.",
                    "image": "/images/sector-social.png",
                    "icon": "/images/sector-icon-building.png"
                },
                {
                    "title": "АДМИНИСТРАТИВНЫЕ И ОБЩЕСТВЕННЫЕ ЗДАНИЯ",
                    "desc": "Бизнес-центры, офисные и городские пространства. Учитываем требования к срокам, согласованиям и точности реализации проекта.",
                    "image": "/images/sector-admin.png",
                    "icon": "/images/sector-icon-factory.png"
                },
                {
                    "title": "ПРОМЫШЛЕННЫЕ И ИНЖЕНЕРНЫЕ ОБЪЕКТЫ",
                    "desc": "Производственные здания, котельные и технические сооружения. Учитываем нагрузки, условия эксплуатации и требования к надёжности.",
                    "image": "/images/sector-industrial.png",
                    "icon": "/images/sector-icon-cube.png"
                }
            ],
            "partner_logos": [
                "/images/logos/logo-fssp.png",
                "/images/logos/logo-sber.png",
                "/images/logos/logo-mchs.png",
                "/images/logos/logo-gazprom.png",
                "/images/logos/logo-tbank.png"
            ]
        }
    },
    {
        "order": 8,
        "section_key": "cases",
        "title": "Выполненные объекты (06 — Кейсы)",
        "data": {
            "title": "ОБЪЕКТЫ, КОТОРЫЕ МЫ ЗАЩИТИЛИ",
            "items": [
                {
                    "title": "БИЗНЕС-ЦЕНТР СБЕРБАНКА",
                    "scope": "Комплексная система безопасности класса А: 48 IP-камер с видеоаналитикой, СКУД на 6 входных групп и интеграция с постом охраны.",
                    "image": "/images/case-1.jpg"
                },
                {
                    "title": "АДМИНИСТРАТИВНЫЙ КОМПЛЕКС ФССП",
                    "scope": "Адресная система пожарной безопасности и турникеты СКУД с биометрическим распознаванием. Полное согласование и сдача органам МЧС.",
                    "image": "/images/case-2.jpg"
                },
                {
                    "title": "РЕГИОНАЛЬНЫЙ ЦОД Т-БАНК",
                    "scope": "Структурированная кабельная система категории 6A, серверные стойки и комплексный видеоконтроль серверных залов с архивом 90 дней.",
                    "image": "/images/case-3.png"
                }
            ]
        }
    },
    {
        "order": 9,
        "section_key": "engineer_cta",
        "title": "Вызов инженера (07 — Форма проекта)",
        "data": {
            "title": "ОБСУДИМ ВАШ ПРОЕКТ?",
            "subtitle": "Опишите задачу — свяжемся, уточним детали и согласуем время осмотра объекта.",
            "engineer_photo": "/images/section07-engineer.jpg",
            "success_bg_image": "/images/success-3d-bg.png",
            "button_text": "ОСТАВИТЬ ЗАЯВКУ"
        }
    },
    {
        "order": 10,
        "section_key": "faq",
        "title": "Часто задаваемые вопросы (07 — FAQ)",
        "data": {
            "title": "ЧАСТЫЕ ВОПРОСЫ",
            "items": [
                {
                    "q": "ВЫЕЗД ИНЖЕНЕРА ДЕЙСТВИТЕЛЬНО БЕСПЛАТНЫЙ?",
                    "a": "Да, инженер выезжает на объект по Владивостоку и пригороду совершенно бесплатно. Он производит точные замеры, выявляет слепые зоны и составляет перечень необходимых работ."
                },
                {
                    "q": "У НАС НЕТ ПРОЕКТА. СДЕЛАЕТЕ САМИ?",
                    "a": "Да, разрабатываем полный комплект проектно-сметной документации: трассировку кабелей, подбор оборудования, схемы подключений и согласование с надзорными органами."
                },
                {
                    "q": "У НАС УЖЕ СТОИТ СИСТЕМА. ВОЗЬМЁТЕСЬ ЗА ОБСЛУЖИВАНИЕ?",
                    "a": "Да, проводим аудит существующей системы, выявляем неисправности, выполняем модернизацию, дооснащение современным оборудованием и берём объект на регламентное техническое обслуживание."
                },
                {
                    "q": "КАКАЯ ГАРАНТИЯ НА РАБОТЫ?",
                    "a": "Предоставляем официальную гарантию 3 года на монтажные и пусконаладочные работы, а также прямую гарантию производителя на всё установленное сертифицированное оборудование."
                },
                {
                    "q": "КАК МОЖНО ОПЛАТИТЬ?",
                    "a": "Работаем с юридическими и физическими лицами по безналичному расчёту с НДС и без НДС, поэтапная оплата по договору: аванс на закупку оборудования и окончательный расчёт после приёмки."
                }
            ]
        }
    },
    {
        "order": 11,
        "section_key": "contacts",
        "title": "Контакты и реквизиты (Подвал)",
        "data": {
            "title": "МОНТАЖНАЯ ИМПЕРИЯ",
            "phone": "+7 (423) 200-00-00",
            "phone_clean": "+74232000000",
            "email": "info@montazh-imperia.ru",
            "address": "г. Владивосток, Приморский край",
            "hours": "ПН-ВС · 9:00-20:00",
            "inn": "ООО «МОНТАЖНАЯ ИМПЕРИЯ» · ИНН 0000000000 · ОГРН 0000000000000",
            "tg_link": "https://t.me/montazh_imperia",
            "wa_link": "https://wa.me/74232000000",
            "footer_logo": "/images/footer-logo-mi.png"
        }
    }
]

async def seed_database(reset: bool = False):
    """
    Initializes tables and populates initial data.
    If reset=True, drops all tables first.
    """
    settings.ensure_directories()

    async with engine.begin() as conn:
        if reset:
            print("[INFO] Сброс базы данных (drop_all)...")
            await conn.run_sync(Base.metadata.drop_all)
        print("[INFO] Создание таблиц (create_all)...")
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Admin user
        stmt = select(AdminUser).where(AdminUser.username == settings.DEFAULT_ADMIN_USERNAME)
        result = await session.execute(stmt)
        admin = result.scalar_one_or_none()

        if not admin:
            admin = AdminUser(
                username=settings.DEFAULT_ADMIN_USERNAME,
                hashed_password=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD.get_secret_value()),
                created_at=datetime.now(timezone.utc)
            )
            session.add(admin)
            print(f"[SUCCESS] Создан администратор: {settings.DEFAULT_ADMIN_USERNAME}")
        else:
            print(f"[INFO] Администратор '{settings.DEFAULT_ADMIN_USERNAME}' уже существует.")

        # 2. Site Content Sections
        for sec in DEFAULT_SECTIONS:
            stmt = select(SiteContent).where(SiteContent.section_key == sec["section_key"])
            res = await session.execute(stmt)
            existing = res.scalar_one_or_none()

            if not existing:
                new_sec = SiteContent(
                    section_key=sec["section_key"],
                    title=sec["title"],
                    order=sec["order"],
                    data=sec["data"],
                    updated_at=datetime.now(timezone.utc)
                )
                session.add(new_sec)
                print(f"[SUCCESS] Добавлена секция #{sec['order']}: {sec['section_key']}")
            else:
                existing.title = sec["title"]
                existing.order = sec["order"]
                existing.data = sec["data"]
                existing.updated_at = datetime.now(timezone.utc)
                print(f"[INFO] Секция '{sec['section_key']}' обновлена эталонными данными.")

        await session.commit()
        print("[SUCCESS] Сидирование базы данных успешно завершено!")

if __name__ == "__main__":
    asyncio.run(seed_database(reset=False))
