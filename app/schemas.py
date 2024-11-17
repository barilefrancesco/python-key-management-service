from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class APIKeyCreate(BaseModel):
    name: str
    expires_at: Optional[datetime] = None

class APIKeyResponse(BaseModel):
    id: int
    name: str
    key: str
    created_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True