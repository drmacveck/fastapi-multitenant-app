from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import models
import schemas


async def get_items_by_tenant(db: AsyncSession, tenant_id: str):
    result = await db.execute(
        select(models.Item).where(models.Item.tenant_id == tenant_id)
    )
    return result.scalars().all()

async def create_item_for_tenant(db: AsyncSession, item: schemas.ItemCreate, tenant_id: str):
    db_item = models.Item(
        name=item.name,
        tenant_id=tenant_id
    )
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

async def get_user_by_email(db: AsyncSession, email: str, tenant_id: str):
    result = await db.execute(
        select(models.User).where(models.User.email == email, models.User.tenant_id == tenant_id)
    )
    return result.scalars().first()

async def create_user(db: AsyncSession, email: str, hashed_password: str, tenant_id: str):
    db_user = models.User(email=email, hashed_password=hashed_password, tenant_id=tenant_id)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
