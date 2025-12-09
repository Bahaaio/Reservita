from typing import Annotated

from app.core import config
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

engine = create_engine(config.DATABASE_URL)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


DBSession = Annotated[Session, Depends(get_session)]
