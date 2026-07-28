from pydantic import BaseModel
from sqlmodel import SQLModel, Field


class Task(SQLModel, table= True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(min_length=3, max_length=55)
    done: bool = Field(default= False)


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=55)


class TaskUpdate(BaseModel):
    title: str = Field(min_length=3, max_length=55)
    done: bool


class TaskPatch(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=55)
    done: bool | None = None


class Stats(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int


class ResetResponse(BaseModel):
    message: str
        