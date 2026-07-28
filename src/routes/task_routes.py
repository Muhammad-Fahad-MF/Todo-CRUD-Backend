from fastapi import APIRouter, HTTPException, status
from src.models.task_models import Task #, Stats, TaskCreate, TaskPatch, TaskUpdate, ResetResponse
from src.services import task_service
from src.db.database import SessionDep

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get(
    "",
    response_model=list[Task],
    summary="Get all tasks",
    description="Fetches all tasks. If search or done query parameters are provided then it fetches only required filtered tasks.",
)
def get_all_tasks(session: SessionDep):
    return task_service.get_all_tasks(session)


# @router.get(
#     "/stats",
#     response_model=Stats,
#     summary="Compute Statistics of tasks",
#     description="Retrieves the stats of all tasks (total, completed, pending).",
# )
# def get_stats():
#     return task_service.get_task_stats()


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
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with ID {id} not found!"
        )
    return task


# @router.post(
#     "",
#     response_model=Task,
#     status_code=status.HTTP_201_CREATED,
#     summary="Create a task",
#     description="Appends a new task in tasks list and assigns it a unique id.",
# )
# def create_task(task: TaskCreate):
#     try:
#         return task_service.create_task(task)
#     except ValueError as err:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
#         ) from err


# @router.put(
#     "/{id}",
#     response_model=Task,
#     summary="Update a task full body",
#     description="Performs a complete replacement of an existing task's properties.",
# )
# def update_task(id: int, new_task: TaskUpdate):
#     try:
#         updated = task_service.update_task(id, new_task)
#         if updated is None:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with ID {id} not found"
#             )
#         return updated
#     except ValueError as err:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
#         ) from err


# @router.patch(
#     "/{id}",
#     response_model=Task,
#     summary="Updates one or more attributes of a task",
#     description="Updates the provided attributes of task (done, title, or both).",
# )
# def patch_task(id: int, task: TaskPatch):
#     try:
#         patched = task_service.patch_task(id, task)
#         if patched is None:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with ID {id} not found"
#             )
#         return patched
#     except ValueError as err:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
#         ) from err


# @router.delete(
#     "/{id}",
#     status_code=status.HTTP_204_NO_CONTENT,
#     summary="Deletes task",
# )
# def delete_task(id: int):
#     success = task_service.delete_task(id)
#     if not success:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with ID {id} not found"
#         )


# @router.post("/reset", response_model=ResetResponse, summary="Reset tasks list to initial state")
# def reset_tasks():
#     task_service.reset_tasks()
#     return ResetResponse(message="Tasks list successfully reset")
