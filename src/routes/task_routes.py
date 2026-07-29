from fastapi import APIRouter, HTTPException, status, Query
from typing import Annotated
from src.models.task_models import (
    Task,
    TaskCreate,
    TaskUpdate,
    TaskPatch,
    SortOrder,
    Stats
)  # , ResetResponse
from src.services import task_service
from src.db.database import SessionDep

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get(
    "",
    response_model=list[Task],
    summary="Get all tasks",
    description="Fetches all tasks. If search or done query parameters are provided then it fetches only required filtered tasks.",
)
def get_all_tasks(
    session: SessionDep,
    search: str | None = Query(
        default=None, min_length=2, max_length=25, pattern=r"^[a-zA-Z0-9_ ]+$"
    ),
    status: bool | None = Query( default = None ),
    sorder: Annotated[SortOrder | None, Query()] = None
):
    return task_service.get_all_tasks(search, status, sorder, session)


@router.get(
    "/stats",
    response_model=Stats,
    summary="Compute Statistics of tasks",
    description="Retrieves the stats of all tasks (total, completed, pending).",
)
def get_stats(session: SessionDep):
    return task_service.get_task_stats(session)


@router.get(
    "/{id}",
    response_model=Task,
    summary="Retrieves a specific task",
    description="Fetches a task from tasks list by its unique id and returns its details.",
)
def get_task(id: int, session: SessionDep):
    task = task_service.get_task_by_id(id, session)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {id} not found!",
        )
    return task


@router.post(
    "",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task",
    description="Appends a new task in tasks list and assigns it a unique id.",
)
def create_task(payload: TaskCreate, session: SessionDep):
    try:
        return task_service.create_task(title=payload.title, session=session)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        ) from err


@router.put(
    "/{id}",
    response_model=Task,
    summary="Update a task full body",
    description="Performs a complete replacement of an existing task's properties.",
)
def update_task(id: int, payload: TaskUpdate, session: SessionDep):
    try:
        updated = task_service.update_task(id, payload, session)
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {id} not found",
            )
        return updated
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        ) from err


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletes task",
)
def delete_task(id: int, session: SessionDep):
    try:
        task_service.delete_task(id, session)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(err)
        ) from err


@router.patch(
    "/{id}",
    response_model=Task,
    summary="Updates one or more attributes of a task",
    description="Updates the provided attributes of task (done, title, or both).",
)
def patch_task(id: int, task: TaskPatch, session: SessionDep):
    try:
        patched = task_service.patch_task(id, task, session)
        if patched is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {id} not found",
            )
        return patched
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        ) from err
