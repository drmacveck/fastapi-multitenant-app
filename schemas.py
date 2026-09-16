
from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    email: str
    tenant_id: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ItemBase(BaseModel):
    name: str

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int
    tenant_id: str
    model_config = ConfigDict(from_attributes=True)
