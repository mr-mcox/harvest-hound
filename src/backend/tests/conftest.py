"""
Pytest fixtures for Harvest Hound backend tests
"""

import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# Add backend to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import models  # noqa: E402
from app import app  # noqa: E402


@pytest.fixture
def test_engine():
    """Create an in-memory SQLite engine for testing"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Enable foreign key support for SQLite (required for CASCADE deletes)
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(test_engine) -> Generator[Session, None, None]:
    """Provide a database session for testing"""
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def client(test_engine, monkeypatch) -> Generator[TestClient, None, None]:
    """Provide a test client with isolated database"""

    def get_test_session() -> Generator[Session, None, None]:
        with Session(test_engine) as session:
            yield session

    # Patch the models module to use test engine
    monkeypatch.setattr(models, "engine", test_engine)

    with TestClient(app) as client:
        yield client
