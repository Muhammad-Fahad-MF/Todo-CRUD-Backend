from pydantic import BaseModel
from sqlmodel import SQLModel, Field, func
from enum import StrEnum
from datetime import datetime, UTC


class Task(SQLModel, table= True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(min_length=3, max_length=55)
    done: bool = Field(default= False)
    created_at: datetime = Field(
        default_factory= lambda: datetime.now(UTC),
        sa_column_kwargs= {"server_default": func.now()},
        nullable = False
    )
    updated_at: datetime = Field(
        default_factory= lambda: datetime.now(UTC),
        sa_column_kwargs= {
            "server_default": func.now(),
            "onupdate": func.now()
        },
        nullable = False
    )


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


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"