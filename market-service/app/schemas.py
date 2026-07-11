from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models import ItemStatus


class ItemCreate(SQLModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    price: float = Field(gt=0)
    seller_name: str = Field(min_length=1, max_length=100)


class ItemUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    price: float | None = Field(default=None, gt=0)
    seller_name: str | None = Field(default=None, min_length=1, max_length=100)
    status: ItemStatus | None = None


class ItemRead(SQLModel):
    id: int
    title: str
    description: str | None
    price: float
    seller_name: str
    status: ItemStatus
    created_at: datetime