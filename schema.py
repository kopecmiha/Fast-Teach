from pydantic.main import BaseModel
from typing import Optional


class PostCreate(BaseModel):
    title: str
    content: str


class PostUpdate(BaseModel):
    id: int
    title: Optional[str]
    content: Optional[str]
