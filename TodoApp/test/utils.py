import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine, text
from sqlalchemy.orm import sessionmaker

from ..database import Base
from ..main import app
from ..models import Todos

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)
client = TestClient(app)


@pytest.fixture
def test_todo():
    todo = Todos(
        complete=False,
        description="Learn everyday",
        priority=False,
        title="Learn to Code",
        user_id=1,
    )

    db = TestingSessionLocal()
    db.add(todo)
    db.commit()

    yield todo

    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()


@pytest.fixture
def test_new_todo_request():
    return {
        "complete": False,
        "description": "New todo description",
        "priority": 5,
        "title": "New Todo!",
    }


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


def override_get_current_user_admin():
    return {"username": "gamoranarreola", "id": 1, "user_role": "admin"}


def override_get_current_user_non_admin():
    return {"username": "gamoranarreola", "id": 1, "user_role": "non-admin"}
