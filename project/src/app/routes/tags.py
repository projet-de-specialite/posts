import fastapi as _fastapi
import sqlalchemy.orm as _orm

import project.src.app.schemas as _schemas
import project.src.app.services.tag as tag_service
from project.src.app.routes.important_constants import (
    SUCCESSFUL_DELETION_MESSAGE_KEY, SUCCESSFUL_DELETION_MESSAGE_VALUE_FOR_TAG)
from project.src.config.db.database import SessionLocal

tags_router = _fastapi.APIRouter(
    prefix="/api/v1/tags",
    tags=["tags"],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@tags_router.get("/", response_model=list[_schemas.Tag])
async def fetch_tags(skip: int = 0, limit: int = 100, db: _orm.Session = _fastapi.Depends(get_db)):
    """
    Fetches all the tags \n
    :return: Get all the tags in the database
    """
    tags = await tag_service.get_tags(db=db, skip=skip, limit=limit)
    return tags


@tags_router.post("/new", response_model=_schemas.Tag)
async def create_tag(tag: _schemas.TagCreate, db: _orm.Session = _fastapi.Depends(get_db)):
    """
    Creates a tag - The tag name must be at least 3 characters long! \n
    :param db: A database session \n
    :param tag: Add a tag to the database \n
    :return: The tag
    """
    db_tag = await tag_service.get_tag_by_slug(db=db, tag_slug=tag.name.lower())

    if db_tag:
        raise _fastapi.HTTPException(
            status_code=400,
            detail=f"Tag { tag.name } already registered"
        )

    return await tag_service.create_tag(db=db, tag=tag)


@tags_router.get("/{tag_slug}", response_model=_schemas.Tag)
async def get_tag(tag_slug: str, db: _orm.Session = _fastapi.Depends(get_db)):
    """
    Gets a single tag using its slug.
    A tag has the following attributes: 
    - **id**
    - **slug**
    - **name**
    - **posts**
    \f
    :param db: A database session
    :param tag_slug: A tag slug - a unique slug & name per tag
    :return: The tag
    """

    db_tag = await tag_service.get_tag_by_slug(db=db, tag_slug=tag_slug)
    if db_tag is None:
        raise _fastapi.HTTPException(
            status_code=404,
            detail=f"The tag with slug: {tag_slug} cannot be found!"
        )

    return db_tag


@tags_router.delete("/delete/{tag_slug}", include_in_schema=False)  
async def delete_tag(tag_slug: str, db: _orm.Session = _fastapi.Depends(get_db)):
    """
    Deletes a single tag by its slug \n
    :param db: A database session \n
    :param tag_slug: A tag slug - a unique name per tag \n
    :return: True
    """
    db_tag = await tag_service.get_tag_by_slug(db=db, tag_slug=tag_slug)
    if db_tag is None:
        raise _fastapi.HTTPException(
            status_code=404,
            detail=f"The tag with slug: {tag_slug} cannot be found!"
        )

    ok = await tag_service.delete_tag_by_slug(db=db, tag_slug=tag_slug)

    if ok is False:
        raise _fastapi.HTTPException(
            status_code=400,
            detail=f"Could not delete the tag with slug: {tag_slug}!"
        )

    return {
        f"{ SUCCESSFUL_DELETION_MESSAGE_KEY }": f"{ SUCCESSFUL_DELETION_MESSAGE_VALUE_FOR_TAG }"
    }
