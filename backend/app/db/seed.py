"""Seed default development user. Run: python -m app.db.seed"""

import asyncio
import uuid

from sqlalchemy import select

from app.core.security import Role, hash_password
from app.db.base import Base
from app.db.session import AsyncSessionLocal, engine
from app.models.database import User


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == "admin@astraos.local")
        )
        if result.scalar_one_or_none():
            print("Seed user already exists")
            return

        user = User(
            id=uuid.uuid4(),
            email="admin@astraos.local",
            hashed_password=hash_password("astraos_dev_2024"),
            role=Role.ADMIN.value,
        )
        session.add(user)
        await session.commit()
        print("Created seed user: admin@astraos.local / astraos_dev_2024")


if __name__ == "__main__":
    asyncio.run(seed())
