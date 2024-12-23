from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from ..database import SessionLocal
from ..models import Todos
from .auth import get_current_user

router = APIRouter(prefix="/todos", tags=["todos"])


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class Todo:
    complete: int
    description: str
    id: int
    priority: int
    title: str

    def __init__(
        self, complete: bool, description: str, id: str, priority: int, title: str
    ):
        self.complete = complete
        self.description = description
        self.id = id
        self.priority = priority
        self.title = title


class TodoRequest(BaseModel):
    complete: bool
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    title: str = Field(min_length=3)

    model_config = {
        "json_schema_extra": {
            "example": {
                "complete": False,
                "description": "A todo description",
                "priority": 1,
                "title": "A todo title",
            }
        }
    }


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )

    return db.query(Todos).filter(Todos.user_id == user.get("id")).all()


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )

    todo = (
        db.query(Todos)
        .filter(Todos.id == id)
        .filter(Todos.user_id == user.get("id"))
        .first()
    )

    if todo is not None:
        return todo

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with ID of {id} not found"
    )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_todo(
    user: user_dependency, db: db_dependency, todo_request: TodoRequest
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )

    todo_model = Todos(**todo_request.model_dump(), user_id=user.get("id"))

    db.add(todo_model)
    db.commit()


@router.put("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    user: user_dependency,
    db: db_dependency,
    todo_request: TodoRequest,
    id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )

    todo_model = (
        db.query(Todos)
        .filter(Todos.id == id)
        .filter(Todos.user_id == user.get("id"))
        .first()
    )

    if todo_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with ID {id} not found"
        )

    todo_model.complete = todo_request.complete
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.title = todo_request.title

    db.add(todo_model)
    db.commit()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )

    todo_model = db.query(Todos).filter(Todos.id == id).first()

    if todo_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with ID {id} not found"
        )

    db.query(Todos).filter(Todos.id == id).delete()
    db.commit()
