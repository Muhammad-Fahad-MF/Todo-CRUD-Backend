from sqlmodel import select, func, col
from src.db.database import Session
from src.models.task_models import Task, SortOrder


def db_get_all(
    user_id: str,
    search: str | None,
    status: bool | None,
    sorder: SortOrder | None,
    session: Session,
) -> list[Task]:
    query = select(Task).where(Task.user_id == user_id)
    if search is not None:
        query = query.where(col(Task.title).ilike(f"%{search}%"))
    if status is not None:
        query = query.where(Task.done == status)
    if sorder is not None:
        order_map = {
            SortOrder.ASC: func.lower(Task.title).asc(),
            SortOrder.DESC: func.lower(Task.title).desc(),
        }
        query = query.order_by(order_map[sorder])
    return list(session.exec(query).all())


def db_get_by_id(task_id: int, user_id: str, session: Session) -> Task | None:
    return session.exec(
        select(Task).where(Task.user_id == user_id, Task.id == task_id)
    ).one_or_none()


def db_create(user_id: str, title: str, done: bool, session: Session) -> Task:
    task = Task(user_id=user_id, title=title, done=done)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def db_update(
    task_id: int, user_id: str, title: str, done: bool, session: Session
) -> Task | None:
    task = session.exec(
        select(Task).where(Task.user_id == user_id, Task.id == task_id)
    ).one_or_none()
    if task is None:
        return None
    task.title = title
    task.done = done
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def db_delete(task_id: int, user_id: str, session: Session) -> bool:
    task = session.exec(
        select(Task).where(Task.user_id == user_id, Task.id == task_id)
    ).one_or_none()
    if task is None:
        return False
    session.delete(task)
    session.commit()
    return True


def db_get_count(user_id: str, session: Session) -> int:
    return session.exec(
        select(func.count()).select_from(Task).where(Task.user_id == user_id)
    ).one()


def db_get_completed_count(user_id: str, session: Session) -> int:
    return session.exec(
        select(func.count()).select_from(Task).where(Task.user_id == user_id, Task.done)
    ).one()
