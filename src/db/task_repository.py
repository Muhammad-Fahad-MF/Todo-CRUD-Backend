from sqlmodel import select, func, col
from src.db.database import Session
from src.models.task_models import Task, SortOrder


def seed_tasks(session: Session):
    count = session.exec(select(func.count(Task.id))).one()
    if count > 0:
        return 
    tasks = [
        Task(title = "Buy Grocery", done = False),
        Task(title = "Read AI Engineering Book", done = False),
        Task(title = "Complete Assignment", done = True)
    ]
    session.add_all(tasks)
    session.commit()


def db_get_all(search: str | None, status: bool | None, sorder: SortOrder | None, session: Session) -> list[Task] | None:
    seed_tasks(session)
    query = select(Task)
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
    return session.exec(query).all()


def db_get_by_id(task_id: int, session: Session) -> Task | None:
    return session.get(Task, task_id)


def db_create(title: str, done: bool, session: Session) -> Task:
    task = Task(title = title, done = done)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def db_update(task_id: int, title: str, done: bool, session: Session) -> Task | None:
    task = session.get(Task, task_id)
    if task is None:
        return None
    task.title = title
    task.done = done
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def db_delete(task_id: int, session: Session) -> bool:
    task = session.get(Task, task_id)
    if task is None:
        return False
    session.delete(task)
    session.commit()
    return True

def db_get_count(session: Session) -> int:
    return session.exec(select(func.count()).select_from(Task)).one()


def db_get_completed_count(session: Session) -> int:
    return session.exec(select(func.count()).select_from(Task).where(Task.done)).one()