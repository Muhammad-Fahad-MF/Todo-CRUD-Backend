from src.db.task_repository import (
    db_create,
    db_delete,
    db_get_all,
    db_get_by_id,
    db_update,
    db_get_count,
    db_get_completed_count,
)
from src.models.task_models import Task, TaskUpdate, TaskPatch, SortOrder, Stats
from sqlmodel import Session


def get_all_tasks(
    user_id: str,
    search: str | None,
    status: bool | None,
    sorder: SortOrder | None,
    session: Session,
) -> list[Task]:
    """Business layer to retrieve all tasks with optional query filters."""
    return db_get_all(
        user_id=user_id, search=search, status=status, sorder=sorder, session=session
    )


def get_task_by_id(user_id: str, task_id: int, session: Session) -> Task | None:
    """Business layer to retrieve a single task by ID."""
    return db_get_by_id(user_id=user_id, task_id=task_id, session=session)


def create_task(user_id: str, title: str, session: Session) -> Task:
    """Business layer to sanitize input and create a new task."""
    clean_title = title.strip()
    if not clean_title:
        raise ValueError("Title cannot be empty")
    return db_create(user_id=user_id, title=clean_title, done=False, session=session)


def update_task(
    user_id: str, task_id: int, task_data: TaskUpdate, session: Session
) -> Task | None:
    """Business layer to validate input and update an existing task."""
    clean_title = task_data.title.strip()
    if not clean_title:
        raise ValueError("Title cannot be empty")
    return db_update(
        user_id=user_id,
        task_id=task_id,
        title=clean_title,
        done=task_data.done,
        session=session,
    )


def delete_task(user_id: str, task_id: int, session: Session):
    """Business layer to delete a task."""
    delete = db_delete(user_id=user_id, task_id=task_id, session=session)
    if not delete:
        raise ValueError(f"Task with {task_id} does not exist")


def patch_task(
    user_id: str, task_id: int, task_data: TaskPatch, session: Session
) -> Task | None:
    """Business layer for partial update (PATCH) merging existing state with new fields."""
    existing_task = db_get_by_id(user_id=user_id, task_id=task_id, session=session)
    if existing_task is None:
        return None

    if task_data.title is None and task_data.done is None:
        raise ValueError("At least one field (title or done) must be provided")

    new_title = existing_task.title
    if task_data.title is not None:
        clean_title = task_data.title.strip()
        if not clean_title:
            raise ValueError("Title cannot be empty")
        new_title = clean_title

    new_done = task_data.done if task_data.done is not None else existing_task.done

    return db_update(
        user_id=user_id,
        task_id=task_id,
        title=new_title,
        done=new_done,
        session=session,
    )


def get_task_stats(user_id: str, session: Session) -> Stats:
    """Business layer to compute task statistics (total, completed, pending)."""
    total_count = db_get_count(user_id=user_id, session=session)
    completed_count = db_get_completed_count(user_id=user_id, session=session)
    return Stats(
        total_tasks=total_count,
        completed_tasks=completed_count,
        pending_tasks=total_count - completed_count,
    )


# def reset_tasks() -> None:
#     """Business layer to reset tasks to initial seeded state."""
#     db_seed_data()
