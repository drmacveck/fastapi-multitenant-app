from pydantic import BaseModel, ConfigDict
from typing import Optional

class ItemBase(BaseModel):
    name: str

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    tenant_id: str

    model_config = ConfigDict(from_attributes=True)
