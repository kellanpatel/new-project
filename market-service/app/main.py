from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import Session

from app.crud import (
    buy_item,
    create_item,
    delete_item,
    get_item,
    list_items,
    update_item,
)
from app.database import create_db_and_tables, get_session
from app.models import Item, ItemStatus
from app.schemas import ItemCreate, ItemRead, ItemUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="MarketFlow Market Service",
    description="Handles marketplace item listings and buying/selling actions.",
    version="0.2.0",
    lifespan=lifespan,
)

SessionDep = Annotated[Session, Depends(get_session)]


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "MarketFlow Market Service is running. Go to /docs"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/items", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_market_item(item_create: ItemCreate, session: SessionDep) -> Item:
    return create_item(session, item_create)


@app.get("/items", response_model=list[ItemRead])
def read_market_items(session: SessionDep) -> list[Item]:
    return list_items(session)


@app.get("/items/{item_id}", response_model=ItemRead)
def read_market_item(item_id: int, session: SessionDep) -> Item:
    item = get_item(session, item_id)

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    return item


@app.put("/items/{item_id}", response_model=ItemRead)
def update_market_item(
    item_id: int,
    item_update: ItemUpdate,
    session: SessionDep,
) -> Item:
    item = get_item(session, item_id)

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    return update_item(session, item, item_update)


@app.post("/items/{item_id}/buy", response_model=ItemRead)
def buy_market_item(item_id: int, session: SessionDep) -> Item:
    item = get_item(session, item_id)

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    if item.status == ItemStatus.SOLD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item has already been sold",
        )

    return buy_item(session, item)


@app.delete("/items/{item_id}", status_code=status.HTTP_200_OK)
def delete_market_item(item_id: int, session: SessionDep) -> dict[str, str]:
    item = get_item(session, item_id)

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    delete_item(session, item)

    return {"message": "Item deleted"}