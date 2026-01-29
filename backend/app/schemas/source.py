from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SourceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    owner: str | None = Field(None, max_length=255)


class SourceUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    owner: str | None = Field(None, max_length=255)
    is_active: bool | None = None


class SourceResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    owner: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
