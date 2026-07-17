from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="Todo CRUD API",
    description="A robust FastAPI implementation of a Todo backend matching REST API conventions.",
    version="1.0.0"
)

# --- Pydantic Models for Validation ---

class Task(BaseModel):
    id: int = Field(..., description="The unique identifier of the task")
    title: str = Field(..., description="The title of the task")
    done: bool = Field(..., description="The status of the task (completed or pending)")

class TaskCreate(BaseModel):
    title: str = Field(..., description="The title of the task", min_length=1)
    done: bool = Field(False, description="Whether the task is completed")

class TaskUpdate(BaseModel):
    title: str = Field(..., description="The updated title of the task", min_length=1)
    done: bool = Field(..., description="The updated status of the task")

class TaskPatch(BaseModel):
    title: str | None = Field(None, description="The updated title of the task", min_length=1)
    done: bool | None = Field(None, description="The updated status of the task")

class TaskStats(BaseModel):
    total: int = Field(..., description="Total number of tasks")
    completed: int = Field(..., description="Number of completed tasks")
    pending: int = Field(..., description="Number of pending tasks")

class RootResponse(BaseModel):
    name: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")
    endpoints: list[str] = Field(..., description="Available API endpoints")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Backend health status")

# --- In-Memory Data Storage ---

# Initializing with 3 generic tasks
tasks: list[Task] = [
    Task(id=1, title="Task 1", done=False),
    Task(id=2, title="Task 2", done=True),
    Task(id=3, title="Task 3", done=False)
]

# ID counter initialized to 3 to match the generic tasks
task_id_counter: int = 3


# --- API Endpoints ---

@app.get("/", response_model=RootResponse, summary="Root information")
def get_root():
    """
    Fetches the API name, version, and the list of available endpoints.
    """
    available_endpoints = [
        "GET /",
        "GET /health",
        "GET /tasks",
        "GET /tasks/{id}",
        "POST /tasks",
        "PUT /tasks/{id}",
        "PATCH /tasks/{id}",
        "DELETE /tasks/{id}",
        "GET /stats",
        "POST /reset"
    ]
    return RootResponse(
        name="Todo CRUD API",
        version="1.0.0",
        endpoints=available_endpoints
    )


@app.get("/health", response_model=HealthResponse, summary="Health status")
def get_health():
    """
    Returns the current health status of the backend.
    """
    return HealthResponse(status="ok")


@app.get("/tasks", response_model=list[Task], summary="Retrieve all tasks")
def get_all_tasks(
    done: bool | None = Query(None, description="Filter tasks by completion status"),
    search: str | None = Query(None, description="Search term to filter tasks by title")
):
    """
    Returns the list of tasks. Allows optional filtering by completion status (done)
    and searching by task title simultaneously.
    """
    filtered_tasks = tasks
    
    if done is not None:
        filtered_tasks = [t for t in filtered_tasks if t.done == done]
        
    if search is not None:
        search_stripped = search.strip().lower()
        if search_stripped:
            filtered_tasks = [t for t in filtered_tasks if search_stripped in t.title.lower()]
            
    return filtered_tasks


@app.get("/tasks/{task_id}", response_model=Task, summary="Retrieve a specific task")
def get_task(task_id: int):
    """
    Retrieves a specific task from the list by its ID.
    Returns 404 if the task is not found.
    """
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task with ID {task_id} not found"
    )


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED, summary="Create a new task")
def create_task(task_in: TaskCreate):
    """
    Creates a new task. Increments the ID counter automatically.
    Returns 201 status code with the created task.
    """
    global task_id_counter
    
    # Validate that title is not empty or just whitespace
    title_clean = task_in.title.strip()
    if not title_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty or whitespace only"
        )
        
    task_id_counter += 1
    new_task = Task(id=task_id_counter, title=title_clean, done=task_in.done)
    tasks.append(new_task)
    return new_task


@app.put("/tasks/{task_id}", response_model=Task, summary="Update a task (Full Update)")
def update_task(task_id: int, task_in: TaskUpdate):
    """
    Updates the entire task with the provided ID using PUT semantics.
    Requires both title and done status. Returns 404 if not found.
    """
    # Validate that title is not empty or just whitespace
    title_clean = task_in.title.strip()
    if not title_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty or whitespace only"
        )

    for index, task in enumerate(tasks):
        if task.id == task_id:
            updated_task = Task(id=task_id, title=title_clean, done=task_in.done)
            tasks[index] = updated_task
            return updated_task
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task with ID {task_id} not found"
    )


@app.patch("/tasks/{task_id}", response_model=Task, summary="Patch a task (Partial Update)")
def patch_task(task_id: int, task_in: TaskPatch):
    """
    Partially updates a task with the provided ID using PATCH semantics.
    Accepts title, done, or both. Returns 404 if not found.
    """
    # Ensure at least one update parameter is provided
    if task_in.title is None and task_in.done is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field ('title' or 'done') must be provided for update"
        )
        
    # Check that if title is provided, it is not empty/whitespace
    title_clean = None
    if task_in.title is not None:
        title_clean = task_in.title.strip()
        if not title_clean:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title cannot be empty or whitespace only"
            )

    for index, task in enumerate(tasks):
        if task.id == task_id:
            new_title = title_clean if title_clean is not None else task.title
            new_done = task_in.done if task_in.done is not None else task.done
            
            updated_task = Task(id=task_id, title=new_title, done=new_done)
            tasks[index] = updated_task
            return updated_task
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task with ID {task_id} not found"
    )


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a task")
def delete_task(task_id: int):
    """
    Deletes a task by ID. Returns 204 status code and no content on success.
    Returns 404 if the task is not found.
    """
    for index, task in enumerate(tasks):
        if task.id == task_id:
            tasks.pop(index)
            return
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task with ID {task_id} not found"
    )


@app.get("/stats", response_model=TaskStats, summary="Tasks statistics")
def get_stats():
    """
    Computes and returns the task statistics: total, completed, and pending tasks.
    """
    total = len(tasks)
    completed = sum(1 for t in tasks if t.done)
    pending = total - completed
    return TaskStats(total=total, completed=completed, pending=pending)


@app.post("/reset", summary="Reset tasks list")
def reset_tasks():
    """
    Serves testing purposes: clears all current tasks and restores the 3 generic tasks.
    Resets the task counter back to 3.
    """
    global tasks, task_id_counter
    tasks = [
        Task(id=1, title="Task 1", done=False),
        Task(id=2, title="Task 2", done=True),
        Task(id=3, title="Task 3", done=False)
    ]
    task_id_counter = 3
    return {"message": "Tasks database reset successfully"}
