import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from app.config import get_settings


def database_available() -> bool:
    try:
        engine = create_engine(get_settings().sqlalchemy_database_url, pool_pre_ping=True)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False


requires_database = pytest.mark.skipif(
    not database_available(),
    reason="PostgreSQL/PostGIS database is not available. Run docker compose up -d and alembic upgrade head.",
)


@pytest.fixture()
def db_session():
    engine = create_engine(get_settings().sqlalchemy_database_url, pool_pre_ping=True)
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = TestingSessionLocal()
    transaction = session.begin()
    try:
        yield session
    finally:
        transaction.rollback()
        session.close()


@pytest.fixture()
def api_base_url() -> str:
    return os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture()
def anyio_backend() -> str:
    return "asyncio"
