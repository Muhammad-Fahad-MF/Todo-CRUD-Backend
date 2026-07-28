from sqlmodel import select, func
from src.db.database import Session
from src.models.task_models import Task


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


def db_get_all(session: Session) -> list[Task] | None:
    seed_tasks(session)
    return session.exec(select(Task)).all()


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

