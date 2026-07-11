from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, status
from sqlmodel import Session

from app.crud import (
    create_activity_log,
    list_activity_logs,
    list_activity_logs_for_item,
)
from app.database import create_db_and_tables, get_session
from app.models import ActivityLog
from app.schemas import ActivityLogCreate, ActivityLogRead


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="MarketFlow Activity Service",
    description="Records important events that happen in the marketplace.",
    version="0.1.0",
    lifespan=lifespan,
)

SessionDep = Annotated[Session, Depends(get_session)]


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "MarketFlow Activity Service is running. Go to /docs."
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/activity",
    response_model=ActivityLogRead,
    status_code=status.HTTP_201_CREATED,
)
def create_activity(
    activity_create: ActivityLogCreate,
    session: SessionDep,
) -> ActivityLog:
    return create_activity_log(session, activity_create)


@app.get("/activity", response_model=list[ActivityLogRead])
def read_activity_logs(session: SessionDep) -> list[ActivityLog]:
    return list_activity_logs(session)


@app.get("/activity/item/{item_id}", response_model=list[ActivityLogRead])
def read_activity_logs_for_item(
    item_id: int,
    session: SessionDep,
) -> list[ActivityLog]:
    return list_activity_logs_for_item(session, item_id)