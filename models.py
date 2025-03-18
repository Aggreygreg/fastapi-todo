from sqlmodel import SQLModel, Field
from typing import Optional

# SQLModel (Database) Models
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    completed: bool = Field(default=False)
    user_id: int = Field(foreign_key="user.id")

# Pydantic (API) Models
class UserCreate(SQLModel):
    username: str
    email: str
    password: str

class UserOut(SQLModel):
    id: int
    username: str
    email: str