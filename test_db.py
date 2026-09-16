import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/app_db"

async def check_db():
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        print("Database Connection Success:", result.scalar() == 1)
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_db())
