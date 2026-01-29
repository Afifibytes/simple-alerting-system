"""Common pagination schemas."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Query parameters for pagination."""

    offset: int = Field(0, ge=0, description="Number of items to skip")
    limit: int = Field(50, ge=1, le=1000, description="Maximum number of items to return")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    items: list[T]
    total: int = Field(..., description="Total number of items matching the query")
    offset: int = Field(..., description="Current offset")
    limit: int = Field(..., description="Current limit")
    has_more: bool = Field(..., description="Whether there are more items after this page")
