from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field


class Task(BaseModel):
    id: int
    title: str = Field(min_length=3, max_length=25)
    done: bool


tasks: list[Task] = []
task_id_count = 0


def clear_and_seed_tasks():
    global tasks
    tasks = []
    tasks.extend(
        [
            Task(id=1, title="Task 1", done=False),
            Task(id=2, title="Task 2", done=True),
            Task(id=3, title="Task 3", done=False),
        ]
    )
    global task_id_count
    task_id_count = 3


@asynccontextmanager
async def lifespan(_app: FastAPI):
    clear_and_seed_tasks()
    yield


app = FastAPI(lifespan=lifespan)


@app.get(
    "/",
    summary="Root route for information on backend",
    description="Retrieved JSON include name, version, and a list of endpoints",
)
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", description="Returns the status of backend", summary="Health Route")
def check_health():
    return {"status": "ok"}


@app.get(
    "/tasks",
    response_model=list[Task],
    summary="Get all tasks",
    description="Fetches all tasks. If search or done status query parameters are provided then it fetches only required filtered tasks",
)
def get_all_tasks(done: bool | None = None, search: str | None = None):
    filtered_list = tasks
    if done is not None:
        filtered_list = [t for t in filtered_list if t.done == done]
    if search is not None:
        filtered_list = [t for t in filtered_list if search.lower() in t.title.lower()]
    return filtered_list


class Stats(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int


@app.get(
    "/tasks/stats",
    response_model=Stats,
    summary="Compute Statistics of tasks",
    description="Retrieves the stats of all tasks save i.e. number of completed tasks, pending tasks, and total tasks",
)
def get_stats():
    total = len(tasks)
    completed = 0
    for t in tasks:
        if t.done:
            completed += 1
    return Stats(
        total_tasks=total, completed_tasks=completed, pending_tasks=total - completed
    )


@app.get(
    "/tasks/{id}",
    response_model=Task,
    summary="Retrieves a specific task",
    description="Fetches a task from tasks list by its unique id and return its details"
)
def get_task(id: int):
    for t in tasks:
        if t.id == id:
            return t
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with {id} Not Found!"
    )


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=25)
    done: bool | None = False


@app.post(
    "/tasks",
    response_model=Task,
    status_code=201,
    summary="Create a task",
    description="Appends a new task in tasks list and assign it a unique id and provided details",
)
def create_task(task: TaskCreate):
    newTitle = task.title.strip()
    if not newTitle:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Title Missing!"
        )
    global task_id_count
    task_id_count += 1
    newTask = Task(id=task_id_count, title=newTitle, done=task.done)
    tasks.append(newTask)
    return newTask


def find_by_id(id: int) -> int:
    for i in range(0, len(tasks)):
        if id == tasks[i].id:
            return i
    return -1


class TaskUpdate(BaseModel):
    title: str = Field(min_length=3, max_length=25)
    done: bool


# task_id = task index in the tasks array
@app.put(
    "/tasks/{id}",
    response_model=Task,
    summary="Update a task full body",
    description="Performs a **complete replacement** of an existing task's properties.",
)
def update_task(id: int, new_task: TaskUpdate):
    new_task.title = new_task.title.strip()
    if not new_task.title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Title Missing!"
        )
    task_id = find_by_id(id)
    if task_id == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with {id} not found"
        )
    tasks[task_id].title = new_task.title
    tasks[task_id].done = new_task.done
    return tasks[task_id]


class TaskPatch(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=25)
    done: bool | None = None


@app.patch(
    "/tasks/{id}",
    response_model=Task,
    summary="Updates one or more attributes of a task",
    description="Updates the provided attribute of task either done or title or both, slightly different from PUT request as PUT requires whole body",
)
def patch_task(id: int, task: TaskPatch):
    task_id = find_by_id(id)
    if task_id == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with {id} not found"
        )
    if task.title is None and task.done is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing title and status!"
        )
    if task.title is not None:
        task.title = task.title.strip()
        if task.title:
            tasks[task_id].title = task.title
    if task.done is not None:
        tasks[task_id].done = task.done
    return tasks[task_id]


@app.delete(
    "/tasks/{id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletes task",
)
def delete_task(id: int):
    task_id = find_by_id(id)
    if task_id == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with {id} not found"
        )
    tasks.pop(task_id)
    return None


@app.post("/tasks/reset")
def reset_tasks():
    clear_and_seed_tasks()
