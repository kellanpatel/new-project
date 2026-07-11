from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.database import get_session
from app.main import app
from app.models import ActivityLog  # noqa: F401 - ensures table is registered


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


def test_create_activity_log():
    with TestClient(app) as client:
        response = client.post(
            "/activity",
            json={
                "event_type": "ITEM_CREATED",
                "item_id": 1,
                "message": "Item 'Gaming Keyboard' was created.",
            },
        )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["event_type"] == "ITEM_CREATED"
    assert data["item_id"] == 1
    assert data["message"] == "Item 'Gaming Keyboard' was created."
    assert "created_at" in data


def test_list_activity_logs():
    with TestClient(app) as client:
        client.post(
            "/activity",
            json={
                "event_type": "ITEM_CREATED",
                "item_id": 1,
                "message": "Item was created.",
            },
        )

        client.post(
            "/activity",
            json={
                "event_type": "ITEM_UPDATED",
                "item_id": 1,
                "message": "Item was updated.",
            },
        )

        response = client.get("/activity")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["event_type"] == "ITEM_CREATED"
    assert data[1]["event_type"] == "ITEM_UPDATED"


def test_list_activity_logs_for_one_item():
    with TestClient(app) as client:
        client.post(
            "/activity",
            json={
                "event_type": "ITEM_CREATED",
                "item_id": 1,
                "message": "Item 1 was created.",
            },
        )

        client.post(
            "/activity",
            json={
                "event_type": "ITEM_CREATED",
                "item_id": 2,
                "message": "Item 2 was created.",
            },
        )

        client.post(
            "/activity",
            json={
                "event_type": "ITEM_SOLD",
                "item_id": 1,
                "message": "Item 1 was sold.",
            },
        )

        response = client.get("/activity/item/1")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["item_id"] == 1
    assert data[1]["item_id"] == 1


def test_activity_log_can_have_no_item_id():
    with TestClient(app) as client:
        response = client.post(
            "/activity",
            json={
                "event_type": "SYSTEM_STARTED",
                "item_id": None,
                "message": "Activity Service started.",
            },
        )

    assert response.status_code == 201

    data = response.json()

    assert data["event_type"] == "SYSTEM_STARTED"
    assert data["item_id"] is None


def test_cannot_create_activity_log_without_message():
    with TestClient(app) as client:
        response = client.post(
            "/activity",
            json={
                "event_type": "ITEM_CREATED",
                "item_id": 1,
                "message": "",
            },
        )

    assert response.status_code == 422


def test_cannot_create_activity_log_without_event_type():
    with TestClient(app) as client:
        response = client.post(
            "/activity",
            json={
                "event_type": "",
                "item_id": 1,
                "message": "Item was created.",
            },
        )

    assert response.status_code == 422


def test_health_check():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}