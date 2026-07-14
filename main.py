from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

class Task(BaseModel):
    id: int
    title: str=Field(min_length=3, max_length=25)
    done: bool

tasks: list[Task] = []
tasks.extend([Task(id=1, title="Task 1", done= False) , Task(id= 2, title="Task 2", done=True), Task(id=3, title="Task 3", done=False)])

app = FastAPI()

@app.get("/")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def check_health():
    return {"status": "ok"}

@app.get("/tasks")
def get_all_tasks():
    return tasks

@app.get("/tasks/{id}")
def get_task(id: int):
    for t in tasks:
        if(t.id == id):
            return t
    raise HTTPException(
        status_code = status.HTTP_404_NOT_FOUND,
        detail =  f"Item with {id} Not Found!"
    )

class TaskCreate(BaseModel):
    title: str
    done: bool | None = False

@app.post("/tasks")
def create_task(task: TaskCreate):
    newTitle = task.title.strip()
    if(not newTitle):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"Title Missing!"
        )
    newTask = Task(id= len(tasks)+1, title= newTitle, done= task.done)
    tasks.append(newTask)
    return newTask
    