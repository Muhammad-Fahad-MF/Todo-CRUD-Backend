from pydantic import BaseModel, Field


class Task(BaseModel):
    id: int
    title: str = Field(min_length=3, max_length=25)
    done: bool


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=25)
    done: bool | None = False


class TaskUpdate(BaseModel):
    title: str = Field(min_length=3, max_length=25)
    done: bool


class TaskPatch(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=25)
    done: bool | None = None


class Stats(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int


class ResetResponse(BaseModel):
    message: str
        