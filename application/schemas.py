from graphene_sqlalchemy import SQLAlchemyObjectType
from pydantic import BaseModel

from models.somemodel import Post
from typing import Optional


class PostSchema(BaseModel):
    title: str
    content: str
    author: Optional[str]


class PostModel(SQLAlchemyObjectType):
    class Meta:
        model = Post

