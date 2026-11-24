#!/usr/bin/env python3
"""
Management CLI Tool for Montazhnaya Imperiya Backend.

Usage:
    python manage.py status               # Check DB connection and table stats
    python manage.py seed                 # Seed default content & admin
    python manage.py reset-db             # Drop all tables and re-seed
    python manage.py create-admin         # Create or update an admin user
    python manage.py export-content       # Export current DB content to JSON file
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add backend directory to path
BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import func, select, text
from app.auth import get_password_hash
from app.config import settings
from app.database import AsyncSessionLocal, Base, engine
from app.models import AdminUser, Lead, SiteContent
from app.seed import seed_database


async def check_status():
    """Prints DB status, WAL pragma check, and record counts."""
    print("=" * 60)
    print("  МОНТАЖНАЯ ИМПЕРИЯ // СТАТУС БАЗЫ ДАННЫХ")
    print("=" * 60)
    print(f"Окружение:        {settings.ENVIRONMENT}")
    print(f"URL подключения:  {settings.DATABASE_URL}")

    try:
        async with engine.connect() as conn:
            # Check SQLite pragmas
            journal_mode = (await conn.execute(text("PRAGMA journal_mode;"))).scalar()
            foreign_keys = (await conn.execute(text("PRAGMA foreign_keys;"))).scalar()
            print(f"Режим журнала:    {journal_mode} (WAL: {'✓ Да' if str(journal_mode).lower() == 'wal' else '✗ Нет'})")
            print(f"Внешние ключи:    {'✓ Включены' if foreign_keys else '✗ Выключены'}")

        async with AsyncSessionLocal() as session:
            admins_count = (await session.execute(select(func.count(AdminUser.id)))).scalar() or 0
            sections_count = (await session.execute(select(func.count(SiteContent.id)))).scalar() or 0
            leads_count = (await session.execute(select(func.count(Lead.id)))).scalar() or 0
            new_leads = (await session.execute(select(func.count(Lead.id)).where(Lead.status == "new"))).scalar() or 0

            print(f"\nЗаписи в базе:")
            print(f"  - Администраторы:  {admins_count}")
            print(f"  - Секции сайта:    {sections_count}")
            print(f"  - Всего заявок:    {leads_count} (новых: {new_leads})")

        print("\n✓ Соединение с базой данных успешно установлено!")
    except Exception as e:
        print(f"\n✗ Ошибка подключения к базе данных: {e}")
        sys.exit(1)


async def create_admin(username: str, password: str):
    """Creates or updates an admin user."""
    async with AsyncSessionLocal() as session:
        stmt = select(AdminUser).where(AdminUser.username == username)
        res = await session.execute(stmt)
        user = res.scalars().first()

        if user:
            user.hashed_password = get_password_hash(password)
            await session.commit()
            print(f"✓ Пароль администратора '{username}' успешно обновлен!")
        else:
            new_user = AdminUser(
                username=username,
                hashed_password=get_password_hash(password),
                created_at=datetime.now(timezone.utc)
            )
            session.add(new_user)
            await session.commit()
            print(f"✓ Администратор '{username}' успешно создан!")


async def export_content(output_file: str = "content_dump.json"):
    """Dumps all site_content records to a JSON file."""
    async with AsyncSessionLocal() as session:
        stmt = select(SiteContent).order_by(SiteContent.order)
        res = await session.execute(stmt)
        records = res.scalars().all()

        dump = {}
        for r in records:
            dump[r.section_key] = {
                "title": r.title,
                "order": r.order,
                "data": r.data,
                "updated_at": r.updated_at.isoformat() if r.updated_at else None
            }

        out_path = BACKEND_DIR / output_file
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(dump, f, ensure_ascii=False, indent=2)

        print(f"✓ Данные {len(records)} секций экспортированы в: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Montazh Imperiya Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # status
    subparsers.add_parser("status", help="Check database connection and table counts")

    # seed
    subparsers.add_parser("seed", help="Initialize tables and seed default content")

    # reset-db
    subparsers.add_parser("reset-db", help="Drop all tables and recreate clean database")

    # create-admin
    admin_parser = subparsers.add_parser("create-admin", help="Create or update admin user")
    admin_parser.add_argument("--username", "-u", required=True, help="Admin username")
    admin_parser.add_argument("--password", "-p", required=True, help="Admin password")

    # export-content
    export_parser = subparsers.add_parser("export-content", help="Export site content to JSON file")
    export_parser.add_argument("--output", "-o", default="content_dump.json", help="Output JSON path")

    args = parser.parse_args()

    if args.command == "status":
        asyncio.run(check_status())
    elif args.command == "seed":
        asyncio.run(seed_database(reset=False))
    elif args.command == "reset-db":
        confirm = input("Вы уверены, что хотите полностью стереть базу данных? (y/N): ")
        if confirm.lower() == "y":
            asyncio.run(seed_database(reset=True))
        else:
            print("Операция отменена.")
    elif args.command == "create-admin":
        asyncio.run(create_admin(args.username, args.password))
    elif args.command == "export-content":
        asyncio.run(export_content(args.output))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
