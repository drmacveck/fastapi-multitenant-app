from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import auth
import crud
import schemas
from database import Base, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="FastAPI Multi-Tenant App", lifespan=lifespan)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if hasattr(auth, "router"):
    app.include_router(auth.router)

@app.get("/items/", response_model=list[schemas.ItemResponse])
async def list_items(
    x_tenant_id: str | None = Header(None, alias="X-Tenant-ID"),
    db: AsyncSession = Depends(get_db)
):
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="Missing tenant header")
    items = await crud.get_items_by_tenant(db, tenant_id=x_tenant_id)
    return items

@app.post("/items/", response_model=schemas.ItemResponse, status_code=201)
async def create_item(
    item_in: schemas.ItemCreate,
    x_tenant_id: str | None = Header(None, alias="X-Tenant-ID"),
    db: AsyncSession = Depends(get_db)
):
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="Missing tenant header")
    return await crud.create_item_for_tenant(db, item=item_in, tenant_id=x_tenant_id)
