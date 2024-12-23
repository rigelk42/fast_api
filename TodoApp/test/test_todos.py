from fastapi import status

from ..main import app
from ..models import Todos
from ..routers.auth import get_current_user
from ..routers.todos import get_db
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user_admin


def test_read_all_authenticated(test_todo):
    response = client.get("/todos/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "complete": False,
            "priority": 0,
            "user_id": 1,
            "description": "Learn everyday",
            "title": "Learn to Code",
            "id": 1,
        }
    ]


def test_read_one_authenticated(test_todo):
    response = client.get("/todos/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "complete": False,
        "priority": 0,
        "user_id": 1,
        "description": "Learn everyday",
        "title": "Learn to Code",
        "id": 1,
    }


def test_read_one_authenticated_not_found(test_todo):
    response = client.get("/todos/2")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Todo with ID of 2 not found"}


def test_create_todo(test_todo, test_new_todo_request):
    response = client.post("/todos/", json=test_new_todo_request)
    todo_id = 2
    assert response.status_code == status.HTTP_201_CREATED
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == todo_id).first()
    assert model.id == todo_id


def test_update_todo(test_todo, test_new_todo_request):
    update_request_data = test_new_todo_request
    update_request_data["title"] = "Change the title"
    response = client.put("/todos/1", json=update_request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == "Change the title"


def test_delete_todo(test_todo):
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is not None and model.id == 1
    response = client.delete("/todos/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None
