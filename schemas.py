from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    tenant_id: str

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    tenant_id: Optional[str] = None

class ItemBase(BaseModel):
    text: str

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int
    tenant_id: str
    owner_id: int

    model_config = ConfigDict(from_attributes=True)

class PaginatedItemResponse(BaseModel):
    items: List[ItemResponse]
    total: int
    page: Optional[int] = 1
    size: Optional[int] = 10
    pages: Optional[int] = 1

    model_config = ConfigDict(from_attributes=True)
