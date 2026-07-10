# MarketFlow Development Plan

A step-by-step milestone checklist for building your Python FastAPI marketplace project from your current working version to a finished first version.

---

## 1. Project Context

You are building a simplified buying and selling marketplace, similar to eBay.

The first version should allow users to:

- create marketplace items
- view marketplace items
- update marketplace items
- delete marketplace items
- mark marketplace items as sold

The project will eventually have two backend services.

### Market Service

The Market Service handles the main marketplace actions.

It is responsible for:

- item creation
- item listing
- item updates
- item deletion
- marking items as sold
- storing item data

### Activity Service

The Activity Service records important events that happen in the marketplace.

Example events:

- `ITEM_CREATED`
- `ITEM_UPDATED`
- `ITEM_SOLD`
- `ITEM_DELETED`

The first version of service-to-service communication will use HTTP.

Later, this can be upgraded to RabbitMQ or Kafka.

---

## 2. Current Status

You have already completed the first working version of the Market Service.

Completed so far:

- FastAPI app created
- `/docs` page works
- item CRUD endpoints work manually
- automated tests run successfully
- `pytest` shows `8 passed`
- app currently stores data in memory using a dictionary

Current milestone:

```text
Milestone 1 complete:
Market Service works with in-memory storage.
```

The main limitation is that the data disappears when the server restarts.

The next major step is replacing in-memory storage with a real database.

---

## 3. Overall Build Order

Build the project in this order:

1. Confirm current Market Service works
2. Commit the current working version to GitHub
3. Add SQLite database support to Market Service
4. Replace in-memory storage with a real `Item` table
5. Update tests to work with the database
6. Clean up Market Service structure
7. Create Activity Service as a second FastAPI app
8. Add `ActivityLog` database table
9. Make Market Service send HTTP requests to Activity Service
10. Test two-service communication manually and automatically
11. Add Dockerfiles
12. Add `docker-compose.yml`
13. Replace SQLite with PostgreSQL inside Docker
14. Add GitHub Actions CI
15. Add README and documentation
16. Later upgrades: users, seller profiles, orders, authentication, Kafka, frontend, deployment

Do not rush to Docker, Kafka, or a frontend yet.

The correct next step is the database version of the Market Service.

---

# Milestone 0: Protect the Current Working Version

## Goal

Save the current working version before making database changes.

This matters because database integration is more likely to break things. A Git commit gives you a safe checkpoint.

## Files/folders to edit

None.

## Commands to run in PowerShell

From the Market Service folder:

```powershell
cd C:\Users\kella\my-new-application\new-project\market-service
git status
```

If this folder is already connected to GitHub:

```powershell
git add .
git commit -m "Create initial FastAPI market service with in-memory storage and tests"
git push
```

If the folder is not connected to GitHub yet:

```powershell
git init
git add .
git commit -m "Create initial FastAPI market service with in-memory storage and tests"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
git push -u origin main
```

Replace `YOUR-USERNAME` and `YOUR-REPO-NAME` with your actual GitHub details.

## How to manually test it

Run the app:

```powershell
python -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Confirm that your endpoints appear.

## How to run automated tests

Stop the server with:

```text
CTRL + C
```

Then run:

```powershell
python -m pytest
```

## What “done” looks like

- [ ] Git commit created
- [ ] code pushed to GitHub
- [ ] `/docs` still works
- [ ] `python -m pytest` still passes

## What to commit

```text
Create initial FastAPI market service with in-memory storage and tests
```

---

# Milestone 1: Confirm Current Market Service Works

## Goal

Confirm the current in-memory version works before replacing storage with a database.

This is a baseline check.

## Files/folders to edit

None.

## Commands to run

```powershell
cd C:\Users\kella\my-new-application\new-project\market-service
.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

## How to manually test it

Open:

```text
http://127.0.0.1:8000/docs
```

Test these endpoints:

```text
POST /items
GET /items
GET /items/{item_id}
PUT /items/{item_id}
POST /items/{item_id}/buy
DELETE /items/{item_id}
```

Use this JSON for `POST /items`:

```json
{
  "title": "Gaming Keyboard",
  "description": "Mechanical keyboard with RGB lighting",
  "price": 49.99,
  "seller_name": "Kellan"
}
```

## How to run automated tests

```powershell
python -m pytest
```

## What “done” looks like

- [ ] app runs
- [ ] `/docs` opens
- [ ] item can be created
- [ ] item can be viewed
- [ ] item can be updated
- [ ] item can be marked as sold
- [ ] item can be deleted
- [ ] tests pass

## What to commit

Only commit if you changed anything.

Suggested commit message:

```text
Confirm initial Market Service behaviour
```

---

# Milestone 2: Add SQLite Database to Market Service

## Goal

Replace temporary in-memory storage with persistent SQLite storage.

The app currently forgets all items when the server stops. SQLite will save items in a local database file called `market.db`.

## Warning

This step may break your tests at first.

That is normal because the tests were written for dictionary storage, not database storage.

## Files/folders to create or edit

Create:

```text
app/database.py
app/models.py
app/schemas.py
app/crud.py
```

Edit:

```text
app/main.py
requirements.txt
.gitignore
```

## Commands to run

From the Market Service folder:

```powershell
cd C:\Users\kella\my-new-application\new-project\market-service
.venv\Scripts\Activate.ps1
pip install sqlmodel
pip freeze > requirements.txt
```

Create the new files:

```powershell
New-Item app\database.py
New-Item app\models.py
New-Item app\schemas.py
New-Item app\crud.py
```

If a file already exists, do not create it again. Just open it in VS Code and edit it.

---

## Code for `app/database.py`

```python
from collections.abc import Generator

from sqlmodel import SQLModel, Session, create_engine


DATABASE_URL = "sqlite:///./market.db"

connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
```

## Why this matters

This creates the database connection and gives the app a reusable database session.

---

## Code for `app/models.py`

```python
from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ItemStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    SOLD = "SOLD"


class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    price: float = Field(gt=0)
    seller_name: str = Field(min_length=1, max_length=100)
    status: ItemStatus = Field(default=ItemStatus.AVAILABLE, index=True)
    created_at: datetime = Field(default_factory=utc_now)
```

## Why this matters

This is your first real database table.

The `Item` class becomes a table in SQLite.

---

## Code for `app/schemas.py`

```python
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
```

## Why this matters

Schemas define what data the API accepts and returns.

This keeps your API shape separate from the database implementation.

---

## Code for `app/crud.py`

```python
from sqlmodel import Session, select

from app.models import Item, ItemStatus
from app.schemas import ItemCreate, ItemUpdate


def create_item(session: Session, item_create: ItemCreate) -> Item:
    item = Item(**item_create.model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def list_items(session: Session) -> list[Item]:
    statement = select(Item).order_by(Item.id)
    return list(session.exec(statement).all())


def get_item(session: Session, item_id: int) -> Item | None:
    return session.get(Item, item_id)


def update_item(session: Session, item: Item, item_update: ItemUpdate) -> Item:
    update_data = item_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(item, field, value)

    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def buy_item(session: Session, item: Item) -> Item:
    item.status = ItemStatus.SOLD
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def delete_item(session: Session, item: Item) -> None:
    session.delete(item)
    session.commit()
```

## Why this matters

This file contains the database actions.

Instead of doing database logic directly inside routes, your route functions call these helper functions.

---

## Code for `app/main.py`

Replace your current `main.py` with this:

```python
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
```

---

## Update `.gitignore`

Add:

```text
*.db
```

## How to manually test it

Run:

```powershell
python -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Create an item.

Stop the server.

Restart the server.

Then open:

```text
http://127.0.0.1:8000/items
```

The item should still be there.

That proves database persistence is working.

## How to run automated tests

Your tests may fail at this point.

That is expected.

The next milestone updates the tests for the database version.

## What “done” looks like

- [ ] `sqlmodel` installed
- [ ] `database.py` created
- [ ] `models.py` created
- [ ] `schemas.py` created
- [ ] `crud.py` created
- [ ] `main.py` updated
- [ ] app runs
- [ ] `market.db` appears
- [ ] item data persists after server restart
- [ ] `*.db` added to `.gitignore`

## What to commit

Do not commit yet if tests are failing.

Wait until Milestone 3.

---

# Milestone 3: Update Tests for the Database Version

## Goal

Update your tests so they work with the database-backed Market Service.

The tests should use a temporary in-memory SQLite database, not your real `market.db` file.

## Warning

This is slightly more advanced than the first tests.

The key idea is that tests temporarily override the normal database connection.

## Files/folders to edit

Edit:

```text
tests/test_items.py
```

## Code for `tests/test_items.py`

Replace the file with this:

```python
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.database import get_session
from app.main import app
from app.models import Item  # noqa: F401 - ensures table is registered


test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def override_get_session():
    with Session(test_engine) as session:
        yield session


def setup_function():
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)
    app.dependency_overrides[get_session] = override_get_session


def teardown_function():
    app.dependency_overrides.clear()


def test_create_item():
    with TestClient(app) as client:
        response = client.post(
            "/items",
            json={
                "title": "Gaming Keyboard",
                "description": "Mechanical keyboard with RGB lighting",
                "price": 49.99,
                "seller_name": "Kellan",
            },
        )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["title"] == "Gaming Keyboard"
    assert data["price"] == 49.99
    assert data["seller_name"] == "Kellan"
    assert data["status"] == "AVAILABLE"


def test_get_all_items():
    with TestClient(app) as client:
        client.post(
            "/items",
            json={
                "title": "Gaming Mouse",
                "description": "Wireless mouse",
                "price": 24.99,
                "seller_name": "Kellan",
            },
        )

        response = client.get("/items")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_one_item():
    with TestClient(app) as client:
        create_response = client.post(
            "/items",
            json={
                "title": "Monitor",
                "description": "24 inch monitor",
                "price": 80.00,
                "seller_name": "Kellan",
            },
        )

        item_id = create_response.json()["id"]
        response = client.get(f"/items/{item_id}")

    assert response.status_code == 200
    assert response.json()["title"] == "Monitor"


def test_update_item():
    with TestClient(app) as client:
        create_response = client.post(
            "/items",
            json={
                "title": "Old Title",
                "description": "Old description",
                "price": 10.00,
                "seller_name": "Kellan",
            },
        )

        item_id = create_response.json()["id"]

        update_response = client.put(
            f"/items/{item_id}",
            json={
                "title": "New Title",
                "price": 15.00,
            },
        )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["title"] == "New Title"
    assert data["price"] == 15.00
    assert data["description"] == "Old description"


def test_buy_item():
    with TestClient(app) as client:
        create_response = client.post(
            "/items",
            json={
                "title": "Football Boots",
                "description": "Used once",
                "price": 30.00,
                "seller_name": "Kellan",
            },
        )

        item_id = create_response.json()["id"]
        buy_response = client.post(f"/items/{item_id}/buy")

    assert buy_response.status_code == 200
    assert buy_response.json()["status"] == "SOLD"


def test_cannot_buy_already_sold_item():
    with TestClient(app) as client:
        create_response = client.post(
            "/items",
            json={
                "title": "Desk",
                "description": "Wooden desk",
                "price": 50.00,
                "seller_name": "Kellan",
            },
        )

        item_id = create_response.json()["id"]

        first_buy_response = client.post(f"/items/{item_id}/buy")
        second_buy_response = client.post(f"/items/{item_id}/buy")

    assert first_buy_response.status_code == 200
    assert second_buy_response.status_code == 400


def test_delete_item():
    with TestClient(app) as client:
        create_response = client.post(
            "/items",
            json={
                "title": "Desk Chair",
                "description": "Comfortable chair",
                "price": 40.00,
                "seller_name": "Kellan",
            },
        )

        item_id = create_response.json()["id"]
        delete_response = client.delete(f"/items/{item_id}")
        get_response = client.get(f"/items/{item_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Item deleted"
    assert get_response.status_code == 404


def test_cannot_create_item_with_negative_price():
    with TestClient(app) as client:
        response = client.post(
            "/items",
            json={
                "title": "Invalid Item",
                "description": "This should fail",
                "price": -10.00,
                "seller_name": "Kellan",
            },
        )

    assert response.status_code == 422
```

## Commands to run

```powershell
python -m pytest
```

## How to manually test it

Run:

```powershell
python -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Create, view, update, buy, and delete an item.

## What “done” looks like

- [ ] tests use temporary SQLite database
- [ ] tests no longer use `items.clear()`
- [ ] tests no longer reset `next_id`
- [ ] all tests pass
- [ ] app still works manually
- [ ] data persists in `market.db`

## What to commit

```powershell
git add .
git commit -m "Replace in-memory item storage with SQLite database"
git push
```

---

# Milestone 4: Clean Up Market Service Structure

## Goal

Make the Market Service easier to understand and maintain.

By now, your folder should look like this:

```text
market-service/
  app/
    __init__.py
    main.py
    database.py
    models.py
    schemas.py
    crud.py
  tests/
    test_items.py
  requirements.txt
  .gitignore
```

## Files/folders to edit

Review these files:

```text
app/main.py
app/database.py
app/models.py
app/schemas.py
app/crud.py
tests/test_items.py
```

## What each file should do

```text
main.py       API routes
models.py     database tables
schemas.py    request and response shapes
crud.py       database actions
database.py   database connection
tests/        automated tests
```

## Commands to run

```powershell
python -m pytest
python -m uvicorn app.main:app --reload
```

## What “done” looks like

- [ ] `main.py` is not too crowded
- [ ] database logic is in `crud.py`
- [ ] database model is in `models.py`
- [ ] request/response models are in `schemas.py`
- [ ] tests pass
- [ ] app runs manually

## What to commit

Only commit if you changed something.

```text
Clean up Market Service structure
```

---

# Milestone 5: Create the Activity Service

## Goal

Create the second backend service.

The Activity Service will record events from the Market Service.

## Warning

This is the first point where your project becomes a multi-service system.

Keep the services separate so you understand what each one is responsible for.

## Files/folders to create

From the project root:

```text
new-project/
  market-service/
  activity-service/
```

## Commands to run

From the project root:

```powershell
cd C:\Users\kella\my-new-application\new-project
mkdir activity-service
cd activity-service
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install fastapi "uvicorn[standard]" sqlmodel pytest httpx
pip freeze > requirements.txt
mkdir app
mkdir tests
New-Item app\__init__.py
New-Item app\main.py
New-Item app\database.py
New-Item app\models.py
New-Item app\schemas.py
New-Item app\crud.py
New-Item tests\test_activity.py
```

## Minimal first code for `activity-service/app/main.py`

Use this temporary starter code first:

```python
from fastapi import FastAPI

app = FastAPI(
    title="MarketFlow Activity Service",
    description="Records important marketplace events.",
    version="0.1.0",
)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "MarketFlow Activity Service is running. Go to /docs"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
```

## Manual test

Run the Activity Service on port `8001`:

```powershell
python -m uvicorn app.main:app --reload --port 8001
```

Open:

```text
http://127.0.0.1:8001/docs
```

## Automated tests

Create a simple first test later, after the `ActivityLog` endpoints exist.

## What “done” looks like

- [ ] `activity-service` folder exists
- [ ] Activity Service has its own `.venv`
- [ ] Activity Service runs on port `8001`
- [ ] `/docs` opens
- [ ] `/health` returns `{"status": "ok"}`

## What to commit

From the project root:

```powershell
git add .
git commit -m "Create Activity Service skeleton"
git push
```

---

# Milestone 6: Add ActivityLog Table and Endpoints

## Goal

Give the Activity Service a real database table for recording marketplace events.

## Files/folders to edit

Inside `activity-service`:

```text
app/database.py
app/models.py
app/schemas.py
app/crud.py
app/main.py
tests/test_activity.py
```

## ActivityLog table design

```text
ActivityLog
- id
- event_type
- item_id
- message
- created_at
```

## Endpoints to add

```text
POST /activity
GET /activity
GET /activity/item/{item_id}
```

## Manual test

Run:

```powershell
python -m uvicorn app.main:app --reload --port 8001
```

Open:

```text
http://127.0.0.1:8001/docs
```

Create an activity log with:

```json
{
  "event_type": "ITEM_CREATED",
  "item_id": 1,
  "message": "Item 'Gaming Keyboard' was created."
}
```

Then run:

```text
GET /activity
GET /activity/item/1
```

## Automated tests

Add tests for:

- creating an activity log
- listing all activity logs
- listing logs for one item
- rejecting invalid activity logs

Run:

```powershell
python -m pytest
```

## What “done” looks like

- [ ] `ActivityLog` database table exists
- [ ] `POST /activity` works
- [ ] `GET /activity` works
- [ ] `GET /activity/item/{item_id}` works
- [ ] tests pass

## What to commit

```text
Add ActivityLog database model and endpoints
```

---

# Milestone 7: Add HTTP Communication Between Services

## Goal

Make the Market Service tell the Activity Service when important item events happen.

Example flow:

```text
User creates item
Market Service stores item
Market Service sends HTTP POST to Activity Service
Activity Service stores activity log
```

## Warning

This step is likely to cause errors at first.

Common issues:

- Activity Service is not running
- wrong port used
- environment variable missing
- request timeout
- wrong endpoint path

## Files/folders to edit

Inside `market-service`:

```text
app/activity_client.py
app/main.py
requirements.txt
tests/test_items.py
```

## Commands to run

Install `httpx` if it is not already installed:

```powershell
pip install httpx
pip freeze > requirements.txt
```

Create:

```powershell
New-Item app\activity_client.py
```

## Code for `app/activity_client.py`

```python
import os

import httpx


ACTIVITY_SERVICE_URL = os.getenv("ACTIVITY_SERVICE_URL")


def send_activity(event_type: str, item_id: int, message: str) -> None:
    if not ACTIVITY_SERVICE_URL:
        return

    payload = {
        "event_type": event_type,
        "item_id": item_id,
        "message": message,
    }

    try:
        httpx.post(
            f"{ACTIVITY_SERVICE_URL}/activity",
            json=payload,
            timeout=2.0,
        )
    except httpx.HTTPError as exc:
        print(f"Activity Service request failed: {exc}")
```

## How to use it in `main.py`

Import it:

```python
from app import activity_client
```

After creating an item, call:

```python
activity_client.send_activity(
    event_type="ITEM_CREATED",
    item_id=item.id,
    message=f"Item '{item.title}' was created.",
)
```

Add similar calls for:

```text
ITEM_UPDATED
ITEM_SOLD
ITEM_DELETED
```

## Manual test

Open two PowerShell windows.

### Terminal 1: Activity Service

```powershell
cd C:\Users\kella\my-new-application\new-project\activity-service
.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --port 8001
```

### Terminal 2: Market Service

```powershell
cd C:\Users\kella\my-new-application\new-project\market-service
.venv\Scripts\Activate.ps1
$env:ACTIVITY_SERVICE_URL="http://127.0.0.1:8001"
python -m uvicorn app.main:app --reload --port 8000
```

Create an item in the Market Service:

```text
http://127.0.0.1:8000/docs
```

Then check the Activity Service:

```text
http://127.0.0.1:8001/docs
```

Run:

```text
GET /activity
```

You should see an `ITEM_CREATED` event.

## Automated tests

Do not require the real Activity Service to be running during Market Service tests.

Instead, mock `send_activity`.

## What “done” looks like

- [ ] both services run at once
- [ ] Market Service runs on `8000`
- [ ] Activity Service runs on `8001`
- [ ] creating an item creates an activity log
- [ ] updating an item creates an activity log
- [ ] buying an item creates an activity log
- [ ] deleting an item creates an activity log
- [ ] tests still pass

## What to commit

```text
Add HTTP activity logging between services
```

---

# Milestone 8: Add Dockerfiles

## Goal

Package each service into a Docker container.

Each service gets its own Dockerfile.

## Warning

Docker errors on Windows are often caused by Docker Desktop not running.

If you see errors about Docker Engine, pipes, or Linux Engine, open Docker Desktop first.

## Files/folders to create

```text
market-service/Dockerfile
activity-service/Dockerfile
```

## Basic Dockerfile for each service

Use this in both services:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Commands to run

Build Market Service:

```powershell
cd C:\Users\kella\my-new-application\new-project\market-service
docker build -t market-service .
```

Build Activity Service:

```powershell
cd C:\Users\kella\my-new-application\new-project\activity-service
docker build -t activity-service .
```

## What “done” looks like

- [ ] Docker Desktop running
- [ ] Market Service image builds
- [ ] Activity Service image builds

## What to commit

```text
Add Dockerfiles for Market Service and Activity Service
```

---

# Milestone 9: Add Docker Compose

## Goal

Run both services with one command.

Eventually, this will also run both databases.

## Files/folders to create

At the project root:

```text
docker-compose.yml
```

## Starter `docker-compose.yml`

```yaml
services:
  activity-service:
    build: ./activity-service
    ports:
      - "8001:8000"

  market-service:
    build: ./market-service
    environment:
      ACTIVITY_SERVICE_URL: http://activity-service:8000
    ports:
      - "8000:8000"
    depends_on:
      - activity-service
```

## Commands to run

From the project root:

```powershell
cd C:\Users\kella\my-new-application\new-project
docker compose up --build
```

## Manual test

Open:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8001/docs
```

Create an item through the Market Service and check whether the Activity Service records it.

## What “done” looks like

- [ ] one command starts both services
- [ ] Market Service reachable on port `8000`
- [ ] Activity Service reachable on port `8001`
- [ ] services communicate inside Docker

## What to commit

```text
Add Docker Compose for local multi-service setup
```

---

# Milestone 10: Add PostgreSQL Through Docker

## Goal

Replace SQLite with PostgreSQL when running through Docker.

SQLite is useful for learning, but PostgreSQL is more realistic for a backend project.

## Warning

This is one of the most likely steps to break.

Common issues:

- wrong database URL
- database not ready before app starts
- wrong service name
- missing PostgreSQL driver
- wrong username or password

## Files/folders to edit

```text
docker-compose.yml
market-service/app/database.py
activity-service/app/database.py
market-service/requirements.txt
activity-service/requirements.txt
```

## Commands to run in each service

```powershell
pip install psycopg2-binary
pip freeze > requirements.txt
```

## Database URL pattern

Market Service:

```text
postgresql+psycopg2://marketuser:marketpass@market-db:5432/marketdb
```

Activity Service:

```text
postgresql+psycopg2://activityuser:activitypass@activity-db:5432/activitydb
```

## Updated Docker Compose should eventually include

```text
market-service
activity-service
market-db
activity-db
```

## Manual test

```powershell
docker compose up --build
```

Open:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8001/docs
```

Create items and activity logs.

Restart Docker Compose and check that data persists.

## What “done” looks like

- [ ] PostgreSQL containers start
- [ ] Market Service connects to Market database
- [ ] Activity Service connects to Activity database
- [ ] items persist in PostgreSQL
- [ ] activity logs persist in PostgreSQL

## What to commit

```text
Use PostgreSQL databases with Docker Compose
```

---

# Milestone 11: Add GitHub Actions CI

## Goal

Automatically run tests whenever you push to GitHub.

This is the CI part of CI/CD.

## Files/folders to create

At project root:

```text
.github/workflows/ci.yml
```

## Basic workflow idea

The workflow should:

```text
checkout code
set up Python
install Market Service dependencies
run Market Service tests
install Activity Service dependencies
run Activity Service tests
build Docker images later
```

## Manual test

Push your code:

```powershell
git add .
git commit -m "Add GitHub Actions CI"
git push
```

Then check the GitHub Actions tab.

## What “done” looks like

- [ ] workflow file exists
- [ ] workflow runs on push
- [ ] Market Service tests pass in GitHub
- [ ] Activity Service tests pass in GitHub

## What to commit

```text
Add GitHub Actions CI for service tests
```

---

# Milestone 12: Add README and Documentation

## Goal

Make the project easy to understand for someone else.

This matters for GitHub, your CV, and interviews.

## Files/folders to edit

```text
README.md
Documentation.md
progress.txt
```

## README should include

```text
Project overview
Architecture
Tech stack
How to run locally
How to run tests
How to run with Docker
API endpoints
Future improvements
```

## Architecture description

Use this wording:

```text
The project is a simplified buying and selling marketplace made from two backend services. The Market Service handles item listings and buying/selling actions. The Activity Service records important marketplace events. In the first version, the services communicate using HTTP. Later, this could be replaced by a message queue such as RabbitMQ or Kafka.
```

## What “done” looks like

- [ ] README explains the project
- [ ] README explains both services
- [ ] README shows how to run locally
- [ ] README shows how to run tests
- [ ] README shows Docker commands
- [ ] README lists future improvements

## What to commit

```text
Add project README and documentation
```

---

# Optional Later Milestones

Only do these after the first version works properly.

## Optional A: Add Users

Add a `User` table:

```text
User
- id
- name
- email
- password
- role
- created_at
```

Start simple. You can keep raw passwords while testing locally, but later replace this with password hashing.

## Optional B: Add Seller Profiles

Add:

```text
SellerProfile
- id
- user_id
- username
- bio
- rating
- created_at
```

Relationship:

```text
A user can become a seller.
A seller profile belongs to one user.
A seller can list many items.
```

## Optional C: Add Orders

Add:

```text
Order
- id
- buyer_id
- item_id
- total_price
- status
- created_at
```

This turns `mark as sold` into a proper purchase flow.

## Optional D: Add Authentication

Add registration, login, password hashing, and JWT tokens.

## Optional E: Replace HTTP with Kafka

Replace:

```text
Market Service -> HTTP request -> Activity Service
```

with:

```text
Market Service -> Kafka topic -> Activity Service
```

## Optional F: Add Frontend

Add a React frontend with pages such as:

```text
Home page
Item list page
Create item page
Item detail page
Seller dashboard
```

## Optional G: Deploy

Deploy the project to a cloud provider.

Possible platforms:

```text
Render
Railway
Fly.io
AWS
Azure
Google Cloud
```

---

# Recommended Git Commit Pattern

Use small commits.

Good examples:

```text
Create initial Market Service
Add item CRUD endpoints
Add pytest tests for item endpoints
Add SQLite database setup
Replace in-memory storage with Item table
Add Activity Service skeleton
Add ActivityLog endpoints
Add HTTP activity logging
Add Dockerfiles
Add Docker Compose
Add GitHub Actions CI
Add README documentation
```

Avoid vague commits like:

```text
finished stuff
fixed things
final version
```

---

# Daily Working Routine

Use this every time you work on the project.

## 1. Go to the right folder

```powershell
cd C:\Users\kella\my-new-application\new-project\market-service
```

## 2. Activate the virtual environment

```powershell
.venv\Scripts\Activate.ps1
```

## 3. Run tests before making changes

```powershell
python -m pytest
```

## 4. Make one small change

Only work on one milestone at a time.

## 5. Run the app

```powershell
python -m uvicorn app.main:app --reload
```

## 6. Test manually

Open:

```text
http://127.0.0.1:8000/docs
```

## 7. Run tests again

```powershell
python -m pytest
```

## 8. Commit

```powershell
git add .
git commit -m "Clear message describing what changed"
git push
```

---

# Immediate Next Step

Your next step is:

```text
Milestone 2: Add SQLite Database to Market Service
```

Before doing that:

- [ ] confirm current tests still pass
- [ ] commit current working version to GitHub
- [ ] install SQLModel

Then begin the database conversion.

Do not move on to Activity Service until:

- [ ] Market Service uses SQLite
- [ ] items persist after server restart
- [ ] tests pass
- [ ] database version is committed to GitHub
