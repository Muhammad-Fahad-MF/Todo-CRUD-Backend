from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from src.routes.task_routes import router as task_router
from src.services.task_service import reset_tasks


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Seed default tasks when application starts
    reset_tasks()
    yield


app = FastAPI(
    title="Todo API",
    version="1.0",
    description="A clean, layered architecture Todo CRUD API built with FastAPI.",
    lifespan=lifespan,
)

# Register routes
app.include_router(task_router)


class RootInfo(BaseModel):
        name: str
        version: str
        endpoints: list[str]


class HealthStatus(BaseModel):
        status: str


@app.get(
    "/",
    response_model=RootInfo,
    summary="Root route for information on backend",
    description="Retrieved JSON includes name, version, and a list of endpoints.",
)
def read_root():
    return RootInfo(name="Task API", version="1.0", endpoints=["/tasks", "/tasks/stats"])


@app.get(
    "/health",
    response_model=HealthStatus,
    summary="Health Route",
    description="Returns the operational status of the backend server.",
)
def check_health():
    return HealthStatus(status="ok")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
