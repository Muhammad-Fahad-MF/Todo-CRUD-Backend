from src.db.task_repository import (
   # db_create,
   # db_delete,
    db_get_all
   # db_get_by_id,
   # db_update
)
from src.models.task_models import Task #, Stats, TaskCreate, TaskPatch, TaskUpdate
from src.db.database import SessionDep


def get_all_tasks(session: SessionDep) -> list[Task]:
    """Business layer to retrieve all tasks with optional query filters."""
    return db_get_all(session)


# def get_task_by_id(task_id: int, session: SessionDep) -> Task | None:
#     """Business layer to retrieve a single task by ID."""
#     return db_get_by_id(task_id, session)


# def create_task(task_data: TaskCreate) -> Task:
#     """Business layer to sanitize input and create a new task."""
#     clean_title = task_data.title.strip()
#     if not clean_title:
#         raise ValueError("Title cannot be empty")

#     is_done = task_data.done if task_data.done is not None else False
#     return db_create(title=clean_title, done=is_done)


# def update_task(task_id: int, task_data: TaskUpdate) -> Task | None:
#     """Business layer to validate input and update an existing task."""
#     clean_title = task_data.title.strip()
#     if not clean_title:
#         raise ValueError("Title cannot be empty")

#     return db_update(task_id=task_id, title=clean_title, done=task_data.done)


# def patch_task(task_id: int, task_data: TaskPatch) -> Task | None:
#     """Business layer for partial update (PATCH) merging existing state with new fields."""
#     existing_task = db_get_by_id(task_id)
#     if existing_task is None:
#         return None

#     if task_data.title is None and task_data.done is None:
#         raise ValueError("At least one field (title or done) must be provided")

#     new_title = existing_task.title
#     if task_data.title is not None:
#         clean_title = task_data.title.strip()
#         if not clean_title:
#             raise ValueError("Title cannot be empty")
#         new_title = clean_title

#     new_done = task_data.done if task_data.done is not None else existing_task.done

#     return db_update(task_id=task_id, title=new_title, done=new_done)


# def delete_task(task_id: int) -> bool:
#     """Business layer to delete a task."""
#     return db_delete(task_id)


# def get_task_stats() -> Stats:
#     """Business layer to compute task statistics (total, completed, pending)."""
#     all_tasks = db_get_all()
#     total = len(all_tasks)
#     completed = sum(1 for t in all_tasks if t.done)
#     return Stats(
#         total_tasks=total,
#         completed_tasks=completed,
#         pending_tasks=total - completed,
#     )


# def reset_tasks() -> None:
#     """Business layer to reset tasks to initial seeded state."""
#     db_seed_data()
