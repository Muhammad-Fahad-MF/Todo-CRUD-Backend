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
