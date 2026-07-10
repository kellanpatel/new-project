from fastapi.testclient import TestClient

import app.main as main_module


client = TestClient(main_module.app)


def setup_function():
    main_module.items.clear()
    main_module.next_id = 1


def test_create_item():
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

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Item deleted"

    get_response = client.get(f"/items/{item_id}")

    assert get_response.status_code == 404


def test_cannot_create_item_with_negative_price():
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