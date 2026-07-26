from src.models.task_models import Task

# In-memory database storage and auto-increment counter
tasks: list[Task] = []
task_id_count: int = 0


def db_seed_data() -> None:
    """Resets memory storage to initial seed data."""
    global tasks, task_id_count
    tasks = [
        Task(id=1, title="Task 1", done=False),
        Task(id=2, title="Task 2", done=True),
        Task(id=3, title="Task 3", done=False),
    ]
    task_id_count = 3


def db_get_all(done: bool | None = None, search: str | None = None) -> list[Task]:
    """Retrieves all tasks from storage with optional filtering."""
    filtered_list = tasks
    if done is not None:
        filtered_list = [t for t in filtered_list if t.done == done]
    if search is not None:
        filtered_list = [t for t in filtered_list if search.lower() in t.title.lower()]
    return filtered_list


def db_get_by_id(task_id: int) -> Task | None:
    """Finds a single task by ID."""
    for task in tasks:
        if task.id == task_id:
            return task
    return None


def db_create(title: str, done: bool) -> Task:
    """Stores a new task with an auto-incremented ID."""
    global task_id_count
    task_id_count += 1
    new_task = Task(id=task_id_count, title=title, done=done)
    tasks.append(new_task)
    return new_task


def db_update(task_id: int, title: str, done: bool) -> Task | None:
    """Replaces an existing task record."""
    for i, task in enumerate(tasks):
        if task.id == task_id:
            updated_task = Task(id=task_id, title=title, done=done)
            tasks[i] = updated_task
            return updated_task
    return None


def db_delete(task_id: int) -> bool:
    """Removes a task record from storage by ID."""
    for i, task in enumerate(tasks):
        if task.id == task_id:
            tasks.pop(i)
            return True
    return False
