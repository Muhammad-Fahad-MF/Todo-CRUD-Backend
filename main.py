from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Annotated
from pydantic.json_schema import SkipJsonSchema

class Task(BaseModel):
    id: int
    title: str=Field(min_length=3, max_length=25)
    done: bool

tasks: list[Task] = []
tasks.extend([Task(id=1, title="Task 1", done= False) , Task(id= 2, title="Task 2", done=True), Task(id=3, title="Task 3", done=False)])
task_id_count = 3

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
    title: str=Field(min_length=3, max_length=25)
    done: bool | None = False

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    newTitle = task.title.strip()
    if(not newTitle):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"Title Missing!"
        )
    global task_id_count
    task_id_count += 1
    newTask = Task(id= task_id_count, title= newTitle, done= task.done)
    tasks.append(newTask)
    return newTask

def find_by_id(id: int) -> int:
    for i in range(0, len(tasks)):
        if(id == tasks[i].id):
            return i
    return -1

class TaskUpdate(BaseModel):
    title: str=Field(min_length=3, max_length=25)
    done: bool 

# task_id = task index in the tasks array
@app.put("/tasks/{id}")
def update_task(id: int, new_task: TaskUpdate):
    task_id = find_by_id(id)
    if(task_id == -1):
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= f"Task with {id} not found"
        )
    tasks[task_id].title = new_task.title
    tasks[task_id].done = new_task.done
    return tasks[task_id]
    

@app.patch("/tasks/{id}")
def patch_task(id: int, title: Annotated[str | SkipJsonSchema[None], Query(min_length=3, max_length=25)] = None, done: Annotated[bool | SkipJsonSchema[None], Query()] = None):
    task_id = find_by_id(id)
    if(task_id == -1):
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= f"Task with {id} not found"
        )
    if title is None and done is None:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= "Missing title and status!"
        )
    if title is not None:
        title = title.strip()
        if title:
            tasks[task_id].title = title
    if done is not None:
        tasks[task_id].done = done
    return tasks[task_id]

@app.delete("/tasks/{id}", status_code=204)
def delete_task(id: int):
    task_id = find_by_id(id)
    if(task_id == -1):
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= f"Task with {id} not found"
        ) 
    tasks.pop(task_id)