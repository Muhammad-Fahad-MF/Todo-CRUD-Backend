from sqlmodel import SQLModel, Session, create_engine
from fastapi import Depends
from typing import Annotated
from collections.abc import Generator
from dotenv import load_dotenv
import os


load_dotenv()

db_url = os.getenv("DB_URL")
engine = create_engine(db_url, echo=True)


def create_db_and_tables():
     SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session]:
     with Session(engine) as session:
          yield session


SessionDep = Annotated[Session, Depends(get_session)]