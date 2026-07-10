from enum import Enum

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field


app = FastAPI(
    title="MarketFlow Market Service",
    description="Handles marketplace item listings and buying/selling actions.",
    version="0.1.0",
)


class ItemStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    SOLD = "SOLD"


class ItemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    price: float = Field(gt=0)
    seller_name: str = Field(min_length=1, max_length=100)


class ItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    price: float | None = Field(default=None, gt=0)
    seller_name: str | None = Field(default=None, min_length=1, max_length=100)
    status: ItemStatus | None = None


class ItemRead(BaseModel):
    id: int
    title: str
    description: str | None
    price: float
    seller_name: str
    status: ItemStatus


items: dict[int, ItemRead] = {}
next_id = 1

@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "MarketFlow Market Service is running. Go to /docs to test the API."
    }

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/items", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(item_create: ItemCreate) -> ItemRead:
    global next_id

    item = ItemRead(
        id=next_id,
        title=item_create.title,
        description=item_create.description,
        price=item_create.price,
        seller_name=item_create.seller_name,
        status=ItemStatus.AVAILABLE,
    )

    items[next_id] = item
    next_id += 1

    return item


@app.get("/items", response_model=list[ItemRead])
def get_items() -> list[ItemRead]:
    return list(items.values())


@app.get("/items/{item_id}", response_model=ItemRead)
def get_item(item_id: int) -> ItemRead:
    item = items.get(item_id)

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    return item


@app.put("/items/{item_id}", response_model=ItemRead)
def update_item(item_id: int, item_update: ItemUpdate) -> ItemRead:
    existing_item = items.get(item_id)

    if existing_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    update_data = item_update.model_dump(exclude_unset=True)
    updated_item = existing_item.model_copy(update=update_data)

    items[item_id] = updated_item

    return updated_item


@app.post("/items/{item_id}/buy", response_model=ItemRead)
def buy_item(item_id: int) -> ItemRead:
    item = items.get(item_id)

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

    updated_item = item.model_copy(update={"status": ItemStatus.SOLD})
    items[item_id] = updated_item

    return updated_item


@app.delete("/items/{item_id}")
def delete_item(item_id: int) -> dict[str, str]:
    item = items.get(item_id)

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    del items[item_id]

    return {"message": "Item deleted"}


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "MarketFlow Market Service is running. Go to /docs"}