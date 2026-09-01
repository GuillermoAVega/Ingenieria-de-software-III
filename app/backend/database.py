from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.pool import StaticPool

DEFAULT_DATABASE_URL = "sqlite:///app/backend/database.db"

Base = declarative_base()


def create_db_engine(database_url: str = DEFAULT_DATABASE_URL) -> Engine:
    if not database_url.startswith("sqlite"):
        return create_engine(database_url)

    connect_args = {"check_same_thread": False}
    if ":memory:" in database_url:
        return create_engine(
            database_url, connect_args=connect_args, poolclass=StaticPool
        )
    return create_engine(database_url, connect_args=connect_args)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


_default_engine = create_db_engine()
_default_session_factory = create_session_factory(_default_engine)


def get_session() -> Generator[Session, None, None]:
    session = _default_session_factory()
    try:
        yield session
    finally:
        session.close()


def create_tables() -> None:
    Base.metadata.create_all(_default_engine)
