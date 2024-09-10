from pydantic import BaseModel
from sqlmodel import SQLModel


class user(SQLModel):
    pass


class token(BaseModel):
    pass
