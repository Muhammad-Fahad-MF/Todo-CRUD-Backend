from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from sqlmodel import text
from pydantic import BaseModel
import uvicorn

from src.routes.task_routes import router as task_router
from src.routes.auth_routes import router as auth_router
from src.routes.public_protected_routes import router as data_router
from src.db.database import create_db_and_tables
from src.db.database import SessionDep



@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Seed default tasks when application starts
    create_db_and_tables()
    yield


app = FastAPI(
    title="Todo API",
    version="1.0",
    description="A clean, layered architecture Todo CRUD API built with FastAPI.",
    lifespan=lifespan,
)

# Register routes
app.include_router(task_router)
app.include_router(auth_router)
app.include_router(data_router)

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
    return RootInfo(name="Task API", version="1.0", endpoints=["/tasks","/tasks/stats"])


@app.get(
    "/health",
    response_model=HealthStatus,
    summary="Health Route",
    description="Returns the operational status of the backend server.",
    status_code=status.HTTP_200_OK
)
def check_health(session: SessionDep):
    try:
        session.exec(text("SELECT 1")).scalar()
        return HealthStatus(status = "ok")
    except Exception as e:
        raise HTTPException (
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        ) from e


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
