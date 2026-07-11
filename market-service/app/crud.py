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