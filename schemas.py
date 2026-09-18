from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any

# ==========================================
# Domain Schemas (Items, Users, Tenants)
# ==========================================

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    tenant_id: str

    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    tenant_id: str

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

# ==========================================
# AI Security Agent Schemas
# ==========================================

class ScanIngestRequest(BaseModel):
    target: str = Field(..., json_schema_extra={"example": "192.168.1.1"})
    raw_nmap_output: str = Field(..., description="Raw text or output from Nmap scan")

class VulnerabilityItem(BaseModel):
    port: int
    service: str
    severity: str = Field(..., json_schema_extra={"example": "HIGH"})
    description: str
    remediation: str

class SecurityReportResponse(BaseModel):
    target: str
    summary: str
    risk_score: int = Field(..., ge=1, le=10)
    vulnerabilities: List[VulnerabilityItem]
    raw_llm_response: Optional[str] = None
