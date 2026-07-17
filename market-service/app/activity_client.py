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
