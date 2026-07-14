from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

class Task(BaseModel):
    id: int
    title: str
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
    