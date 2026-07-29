import sqlite3
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

# Database file path
DB_FILE = "tasks.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL
        )
    """)
    conn.commit()
    
    # Seed 3 tasks if database table is empty
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.executemany(
            "INSERT INTO tasks (id, title, done) VALUES (?, ?, ?)",
            [
                (1, "Task 1", 0),
                (2, "Task 2", 1),
                (3, "Task 3", 0)
            ]
        )
        conn.commit()
    conn.close()

# Database initialization on application startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

# Initialize DB immediately on module load
init_db()

app = FastAPI(
    title="Todo CRUD API",
    description="A robust FastAPI implementation of a Todo backend matching REST API conventions backed by SQLite.",
    version="1.0.0",
    lifespan=lifespan
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
        "GET /stats"
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
    search: str | None = Query(None, description="Search term to filter tasks by title"),
    sort_by: str | None = Query(None, description="Field to sort by (e.g. 'title' or 'id')"),
    order: str = Query("asc", description="Sort order: 'asc' or 'desc'")
):
    """
    Returns the list of tasks. Allows optional filtering by completion status (done),
    searching by task title, and sorting by fields (e.g. title) in asc or desc order.
    """
    effective_order = order.lower()
    if effective_order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order option. Must be 'asc' or 'desc'."
        )

    query = "SELECT id, title, done FROM tasks WHERE 1=1"
    params = []

    if done is not None:
        query += " AND done = ?"
        params.append(1 if done else 0)

    if search is not None:
        search_stripped = search.strip()
        if search_stripped:
            query += " AND LOWER(title) LIKE ?"
            params.append(f"%{search_stripped.lower()}%")

    if sort_by is not None:
        sort_field = sort_by.strip().lower()
        if sort_field == "title":
            query += f" ORDER BY LOWER(title) {effective_order.upper()}, id ASC"
        elif sort_field == "id":
            query += f" ORDER BY id {effective_order.upper()}"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort_by field '{sort_by}'. Allowed fields are 'title' and 'id'."
            )
    else:
        query += " ORDER BY id ASC"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [Task(id=row["id"], title=row["title"], done=bool(row["done"])) for row in rows]


@app.get("/tasks/{task_id}", response_model=Task, summary="Retrieve a specific task")
def get_task(task_id: int):
    """
    Retrieves a specific task from the database by its ID.
    Returns 404 if the task is not found.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

    return Task(id=row["id"], title=row["title"], done=bool(row["done"]))


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED, summary="Create a new task")
def create_task(task_in: TaskCreate):
    """
    Creates a new task in SQLite database.
    Returns 201 status code with the created task.
    """
    title_clean = task_in.title.strip()
    if not title_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty or whitespace only"
        )

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (title_clean, 1 if task_in.done else 0)
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return Task(id=new_id, title=title_clean, done=task_in.done)


@app.put("/tasks/{task_id}", response_model=Task, summary="Update a task (Full Update)")
def update_task(task_id: int, task_in: TaskUpdate):
    """
    Updates the entire task with the provided ID using PUT semantics.
    Requires both title and done status. Returns 404 if not found.
    """
    title_clean = task_in.title.strip()
    if not title_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty or whitespace only"
        )

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (title_clean, 1 if task_in.done else 0, task_id)
    )
    conn.commit()
    conn.close()

    return Task(id=task_id, title=title_clean, done=task_in.done)


@app.patch("/tasks/{task_id}", response_model=Task, summary="Patch a task (Partial Update)")
def patch_task(task_id: int, task_in: TaskPatch):
    """
    Partially updates a task with the provided ID using PATCH semantics.
    Accepts title, done, or both. Returns 404 if not found.
    """
    if task_in.title is None and task_in.done is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field ('title' or 'done') must be provided for update"
        )

    title_clean = None
    if task_in.title is not None:
        title_clean = task_in.title.strip()
        if not title_clean:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title cannot be empty or whitespace only"
            )

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()

    if row is None:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

    new_title = title_clean if title_clean is not None else row["title"]
    new_done = (1 if task_in.done else 0) if task_in.done is not None else row["done"]

    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (new_title, new_done, task_id)
    )
    conn.commit()
    conn.close()

    return Task(id=task_id, title=new_title, done=bool(new_done))


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a task")
def delete_task(task_id: int):
    """
    Deletes a task by ID. Returns 204 status code and no content on success.
    Returns 404 if the task is not found.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
    if cursor.fetchone() is None:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


@app.get("/stats", response_model=TaskStats, summary="Tasks statistics")
def get_stats():
    """
    Computes and returns the task statistics: total, completed, and pending tasks.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            COUNT(*) as total, 
            SUM(CASE WHEN done = 1 THEN 1 ELSE 0 END) as completed 
        FROM tasks
    """)
    row = cursor.fetchone()
    conn.close()

    total = row["total"] if row and row["total"] is not None else 0
    completed = row["completed"] if row and row["completed"] is not None else 0
    pending = total - completed

    return TaskStats(total=total, completed=completed, pending=pending)
