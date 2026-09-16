from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import models, schemas, auth

async def get_user_by_email(db: AsyncSession, email: str, tenant_id: str):
    result = await db.execute(
        select(models.User)
        .filter(models.User.email == email, models.User.tenant_id == tenant_id)
    )
    return result.scalars().first()

async def get_user_by_username(db: AsyncSession, username: str, tenant_id: str):
    result = await db.execute(
        select(models.User)
        .filter(models.User.username == username, models.User.tenant_id == tenant_id)
    )
    return result.scalars().first()

async def create_user(db: AsyncSession, user: schemas.UserCreate, tenant_id: str):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        tenant_id=tenant_id,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
