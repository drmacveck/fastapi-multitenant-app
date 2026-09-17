from typing import List, Optional
from fastapi import FastAPI, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import crud
import schemas
import rate_limit
from database import get_db

app = FastAPI(title="Multi-Tenant Platform")


async def get_tenant_id(x_tenant_id: Optional[str] = Header(None)) -> str:
    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Tenant-ID header is required",
        )
    return x_tenant_id


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post(
    "/items/",
    response_model=schemas.Item,
    status_code=status.HTTP_201_CREATED,
)
async def create_item(
    item: schemas.ItemCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
    _rate_check=Depends(rate_limit.check_rate_limit)
    if hasattr(rate_limit, "check_rate_limit")
    else None,
):
    return await crud.create_item_for_tenant(
        db=db, item=item, tenant_id=tenant_id
    )


@app.get("/items/", response_model=List[schemas.Item])
async def read_items(
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
    _rate_check=Depends(rate_limit.check_rate_limit)
    if hasattr(rate_limit, "check_rate_limit")
    else None,
):
    return await crud.get_items_by_tenant(db=db, tenant_id=tenant_id)
