from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ActivityLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    event_type: str = Field(index=True, min_length=1, max_length=100)
    item_id: int | None = Field(default=None, index=True)
    message: str = Field(min_length=1, max_length=500)
    created_at: datetime = Field(default_factory=utc_now)