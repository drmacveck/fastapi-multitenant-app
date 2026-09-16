from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

import database, models, schemas, crud, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Safe async schema creation on startup
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield

app = FastAPI(title="Multi-Tenant FastAPI App", lifespan=lifespan)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    db: AsyncSession = Depends(database.get_db)
) -> models.User:
    payload = auth.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email: str = payload.get("sub")
    token_tenant_id: str = payload.get("tenant_id")
    
    if not email or token_tenant_id != x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant scope mismatch or invalid credentials"
        )
        
    user = await crud.get_user_by_email(db, email=email, tenant_id=x_tenant_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/register", response_model=schemas.UserResponse, status_code=201)
async def register(
    user_in: schemas.UserCreate,
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    db: AsyncSession = Depends(database.get_db)
):
    existing_user = await crud.get_user_by_email(db, email=user_in.email, tenant_id=x_tenant_id)
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail="Email already registered for this tenant"
        )
    
    return await crud.create_user(db=db, user=user_in, tenant_id=x_tenant_id)

@app.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    x_tenant_id: str = Header(..., alias="X-Tenant-ID"),
    db: AsyncSession = Depends(database.get_db)
):
    user = await crud.get_user_by_email(db, email=form_data.username, tenant_id=x_tenant_id)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(
        data={"sub": user.email, "tenant_id": user.tenant_id}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user
