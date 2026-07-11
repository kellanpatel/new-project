from datetime import datetime

from sqlmodel import Field, SQLModel


class ActivityLogCreate(SQLModel):
    event_type: str = Field(min_length=1, max_length=100)
    item_id: int | None = Field(default=None)
    message: str = Field(min_length=1, max_length=500)


class ActivityLogRead(ActivityLogCreate):
    id: int
    created_at: datetime