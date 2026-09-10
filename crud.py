from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
import models, schemas, auth

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: schemas.UserCreate, tenant_id: str):
    hashed_pw = auth.get_password_hash(user.password)
    db_user = models.User(tenant_id=tenant_id, email=user.email, hashed_password=hashed_pw)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def create_user_item(db: AsyncSession, item: schemas.ItemCreate, user_id: int, tenant_id: str):
    item_data = item.model_dump() if hasattr(item, "model_dump") else item.dict()
    db_item = models.Item(**item_data, owner_id=user_id, tenant_id=tenant_id)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

async def get_items(db: AsyncSession, user_id: int, tenant_id: str, q: Optional[str] = None, skip: int = 0, limit: int = 10):
    query = select(models.Item).where(models.Item.owner_id == user_id, models.Item.tenant_id == tenant_id)
    
    if q:
        query = query.where(models.Item.text.ilike(f"%{q}%"))
    
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    paginated_query = query.offset(skip).limit(limit)
    items_result = await db.execute(paginated_query)
    items = items_result.scalars().all()

    return {"total": total, "items": items}
