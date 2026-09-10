from fastapi import FastAPI, Request, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import models, database, auth, schemas, crud

app = FastAPI(title="Multi-Tenant Async FastAPI Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": {"code": exc.status_code, "message": exc.detail}},
        headers=getattr(exc, "headers", None)
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "error": {"code": 422, "message": "Validation Error", "details": exc.errors()}},
    )

@app.get("/healthz", status_code=200)
async def healthz():
    return {"status": "ok"}

@app.get("/readyz", status_code=200)
async def readyz(db: AsyncSession = Depends(database.get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

@app.post("/register", response_model=schemas.UserResponse, status_code=201)
async def register(
    user: schemas.UserCreate, 
    tenant_id: str = Depends(auth.get_tenant_id),
    db: AsyncSession = Depends(database.get_db)
):
    db_user = await crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud.create_user(db=db, user=user, tenant_id=tenant_id)

@app.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    tenant_id: str = Depends(auth.get_tenant_id),
    db: AsyncSession = Depends(database.get_db)
):
    user = await auth.authenticate_user(db, form_data.username, form_data.password)
    if not user or user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email, password, or tenant context",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.email, "tenant_id": tenant_id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/items", response_model=schemas.ItemResponse, status_code=201)
async def create_item(
    item: schemas.ItemCreate, 
    current_user: models.User = Depends(auth.get_current_user), 
    db: AsyncSession = Depends(database.get_db)
):
    return await crud.create_user_item(db=db, item=item, user_id=current_user.id, tenant_id=current_user.tenant_id)

@app.get("/items", response_model=schemas.PaginatedItemResponse)
async def read_items(
    q: str = None, 
    skip: int = 0, 
    limit: int = 10, 
    current_user: models.User = Depends(auth.get_current_user), 
    db: AsyncSession = Depends(database.get_db)
):
    return await crud.get_items(db, user_id=current_user.id, tenant_id=current_user.tenant_id, q=q, skip=skip, limit=limit)
