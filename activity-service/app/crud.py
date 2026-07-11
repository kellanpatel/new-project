from sqlmodel import Session, select

from app.models import ActivityLog
from app.schemas import ActivityLogCreate


def create_activity_log(
    session: Session,
    activity_create: ActivityLogCreate,
) -> ActivityLog:
    activity_log = ActivityLog(**activity_create.model_dump())

    session.add(activity_log)
    session.commit()
    session.refresh(activity_log)

    return activity_log


def list_activity_logs(session: Session) -> list[ActivityLog]:
    statement = select(ActivityLog).order_by(ActivityLog.id)

    return list(session.exec(statement).all())


def list_activity_logs_for_item(
    session: Session,
    item_id: int,
) -> list[ActivityLog]:
    statement = (
        select(ActivityLog)
        .where(ActivityLog.item_id == item_id)
        .order_by(ActivityLog.id)
    )

    return list(session.exec(statement).all())