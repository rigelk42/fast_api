from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from .database import Base


class Users(Base):
    __tablename__ = "users"

    email = Column(String, unique=True)
    first_name = Column(String)
    hashed_password = Column(String)
    id = Column(Integer, primary_key=True, index=True)
    is_active = Column(Boolean, default=True)
    last_name = Column(String)
    role = Column(String)
    username = Column(String, unique=True)


class Todos(Base):
    __tablename__ = "todos"

    complete = Column(Boolean, default=False)
    description = Column(String)
    id = Column(Integer, primary_key=True, index=True)
    priority = Column(Integer)
    title = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
