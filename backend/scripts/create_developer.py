"""
Create Developer Account
========================
Creates a new user with role='developer', or promotes an existing
user to developer role.

Usage
-----
  # Create a new developer account
  python scripts/create_developer.py --username devadmin --email dev@mediplant.com --password DevPass123

  # Promote an existing user by email
  python scripts/create_developer.py --promote --email existing@user.com

Run from the backend/ directory.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import select, update
from config.database import async_session_maker, init_db
from models.user import User
from services.auth_service import AuthService


async def create_developer(username: str, email: str, password: str) -> None:
    await init_db()
    async with async_session_maker() as session:
        # Check for conflicts
        existing = (await session.execute(
            select(User).where(User.email == email.lower().strip())
        )).scalars().first()

        if existing:
            if existing.role == "developer":
                print(f"[INFO] '{existing.username}' is already a developer.")
                return
            # Promote existing user
            existing.role = "developer"
            await session.commit()
            print(f"[OK] Promoted existing user '{existing.username}' to developer.")
            return

        hashed = AuthService.hash_password(password)
        dev_user = User(
            username=username,
            email=email.lower().strip(),
            hashed_password=hashed,
            is_active=True,
            role="developer",
        )
        session.add(dev_user)
        await session.commit()
        await session.refresh(dev_user)
        print(f"[OK] Developer account created:")
        print(f"     ID       : {dev_user.id}")
        print(f"     Username : {dev_user.username}")
        print(f"     Email    : {dev_user.email}")
        print(f"     Role     : {dev_user.role}")


async def promote_user(email: str) -> None:
    await init_db()
    async with async_session_maker() as session:
        user = (await session.execute(
            select(User).where(User.email == email.lower().strip())
        )).scalars().first()

        if user is None:
            print(f"[ERROR] No user found with email '{email}'.")
            sys.exit(1)

        if user.role == "developer":
            print(f"[INFO] '{user.username}' is already a developer.")
            return

        user.role = "developer"
        await session.commit()
        print(f"[OK] Promoted '{user.username}' (id={user.id}) to developer.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or promote a developer account")
    parser.add_argument("--promote", action="store_true",
                        help="Promote an existing user to developer instead of creating one")
    parser.add_argument("--username", default="devadmin", help="Username for new account")
    parser.add_argument("--email", required=True, help="Email address")
    parser.add_argument("--password", default=None,
                        help="Password (required unless --promote)")

    args = parser.parse_args()

    if args.promote:
        asyncio.run(promote_user(args.email))
    else:
        if not args.password:
            parser.error("--password is required when creating a new account")
        asyncio.run(create_developer(args.username, args.email, args.password))


if __name__ == "__main__":
    main()
