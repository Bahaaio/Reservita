from typing import Annotated

from app.core.config import settings
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, echo=False)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


DBSession = Annotated[Session, Depends(get_session)]
