from fastapi import FastAPI, status
from fastapi.openapi.utils import get_openapi
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

app = FastAPI(
    title="Multi-Tenant Platform API",
    description="Asynchronous multi-tenant backend with JWT authentication, Redis rate limiting, and PostgreSQL isolation.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- Success Schemas ---
class TokenResponse(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field(default="bearer", example="bearer")

class TenantInfoResponse(BaseModel):
    tenant_id: str = Field(..., example="tenant-alpha")
    name: str = Field(..., example="Alpha Corporation")
    status: str = Field(..., example="active")

# --- Specific Error Schemas ---
class InvalidCredentialsResponse(BaseModel):
    detail: str = Field(..., example="Invalid username or password")

class MissingTokenResponse(BaseModel):
    detail: str = Field(..., example="Not authenticated: Bearer token is missing or expired")

class MissingTenantHeaderResponse(BaseModel):
    detail: str = Field(..., example="Header 'X-Tenant-ID' is required for tenant context")

class TenantNotFoundResponse(BaseModel):
    detail: str = Field(..., example="Tenant 'tenant-alpha' does not exist")

class RateLimitResponse(BaseModel):
    detail: str = Field(..., example="Rate limit exceeded: 5 requests per minute allowed")

# --- Custom OpenAPI Generator ---
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    components = openapi_schema.setdefault("components", {})
    components["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT access token to authenticate."
        }
    }

    for path in openapi_schema.get("paths", {}).values():
        for method in path.values():
            if isinstance(method, dict):
                method.setdefault("parameters", []).append({
                    "name": "X-Tenant-ID",
                    "in": "header",
                    "required": True,
                    "schema": {"type": "string"},
                    "description": "Tenant identifier for data isolation"
                })

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# --- Root Redirect ---
@app.get("/", include_in_schema=False)
async def root_redirect():
    """Redirect root path to interactive Swagger docs."""
    return RedirectResponse(url="/docs")

# --- Application Routes ---
@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Health check endpoint"
)
async def health_check():
    """Returns application health status."""
    return {"status": "healthy"}

@app.post(
    "/api/v1/auth/token",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    tags=["Authentication"],
    summary="Generate JWT access token",
    responses={
        400: {"model": MissingTenantHeaderResponse, "description": "Missing Tenant Header"},
        401: {"model": InvalidCredentialsResponse, "description": "Invalid Credentials"},
        429: {"model": RateLimitResponse, "description": "Rate Limit Exceeded"}
    }
)
async def login():
    """Authenticates tenant user and returns JWT token."""
    return {"access_token": "mock-jwt-token-xyz", "token_type": "bearer"}

@app.get(
    "/api/v1/tenant/me",
    response_model=TenantInfoResponse,
    status_code=status.HTTP_200_OK,
    tags=["Tenant"],
    summary="Get current tenant information",
    responses={
        400: {"model": MissingTenantHeaderResponse, "description": "Missing Tenant Header"},
        401: {"model": MissingTokenResponse, "description": "Unauthorized"},
        404: {"model": TenantNotFoundResponse, "description": "Tenant Not Found"}
    }
)
async def get_tenant_info():
    """Retrieves context metadata for the requesting tenant."""
    return {"tenant_id": "tenant-alpha", "name": "Alpha Corporation", "status": "active"}
