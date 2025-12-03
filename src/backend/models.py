"""
Database setup and models for Harvest Hound
"""

from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine, text

# SQLite database
engine = create_engine("sqlite:///harvest.db")


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions"""
    with Session(engine) as session:
        yield session


def db_health() -> bool:
    """Health check - verify database connectivity"""
    with Session(engine) as session:
        result = session.exec(text("SELECT 1"))
        row = result.one()
        return row[0] == 1


# Create tables (none yet, but ready for models)
SQLModel.metadata.create_all(engine)
