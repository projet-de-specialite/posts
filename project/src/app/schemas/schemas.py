import datetime as _datetime
import uuid

import pydantic as _pydantic


DEFAULT_DATETIME: _datetime.datetime = _datetime.datetime(1, 1, 1, 0, 0, 0, 0)
TAG_MIN_LENGTH = 3


class TagBase(_pydantic.BaseModel):
    """
    The class used for creating/reading a post data - contains useful attributes for C/R
    """
    name: str = _pydantic.Field(..., min_length=TAG_MIN_LENGTH)

    class Config:
        orm_mode = True


class PostBase(_pydantic.BaseModel):
    """
    The class used for creating/reading a post data - contains useful attributes for C/R
    """
    image: str
    caption: str | None = None
    tags: list[TagBase] = []
    published: bool = False
    owner_id: int

    class Config:
        orm_mode = True


class TagCreate(TagBase):
    """
    The class used for creation - can contain any additional attribute needed for creation
    """
    pass


class PostCreate(PostBase):
    """
    The class used for creation - can contain any additional attribute needed for creation
    """
    # store the image in the bucket, get the public uri and store it in the image attribute
    pass


class Tag(TagBase):
    """
    The class used for reading a post data when returned from the api
    """
    id: uuid.UUID
    slug: str
    posts: list[PostBase]
    created_on: _datetime.datetime


# class PostUpdate(PostBase):
class PostUpdate(_pydantic.BaseModel):
    """
    The class used for updating a post
    """
    caption: str | None
    tags: list[TagBase] | None
    published: bool | None = False


class Post(PostBase):
    """
    The class used for reading a post data when returned from the api
    """
    id: uuid.UUID
    likes: int
    comments: list[int]
    published_on: _datetime.datetime
    created_on: _datetime.datetime
    updated_on: _datetime.datetime
