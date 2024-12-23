from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from starlette import status

from ..database import SessionLocal
from ..models import Todos
from .auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )

    return db.query(Todos).all()


@router.delete("/todo/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )

    todo_model = db.query(Todos).filter(Todos.id == id).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail=f"Todo with ID {id} not found")

    db.query(Todos).filter(Todos.id == id).delete()
    db.commit()
