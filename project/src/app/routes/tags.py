import fastapi as _fastapi
import sqlalchemy.orm as _orm

import project.src.app.schemas as _schemas
import project.src.app.services.tag as tag_service
from project.src.app.routes.shared_constants_and_methods import (
    SUCCESSFUL_DELETION_MESSAGE_KEY, SUCCESSFUL_DELETION_MESSAGE_VALUE_FOR_TAG,
    get_object_cannot_be_found_detail_message, ObjectType, get_tag_already_exists_detail_message,
    get_object_cannot_be_deleted_detail_message, get_search_characters_length_must_be_greater_than_three,
    VALUE_LENGTH_ERROR_STATUS_CODE, TAG_ALREADY_EXISTS_STATUS_CODE, OBJECT_CANNOT_BE_FOUND_STATUS_CODE,
    OBJECT_CANNOT_BE_DELETED_STATUS_CODE)
from project.src.config.db.database import SessionLocal

tags_router = _fastapi.APIRouter(
    prefix="/api/v1/tags",
    tags=["tags"],
)

SEARCH_CHARACTERS_MIN_LENGTH = 3


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


@tags_router.get("/search/{characters}", response_model=list[_schemas.Tag])
async def search_tags(characters: str, skip: int = 0, limit: int = 100, db: _orm.Session = _fastapi.Depends(get_db)):
    """
    Fetches all the tags with names containing the given characters \n
    :return: Get all the tags in the database with names containing the given characters
    """
    if len(characters) < SEARCH_CHARACTERS_MIN_LENGTH:
        raise _fastapi.HTTPException(
            status_code=VALUE_LENGTH_ERROR_STATUS_CODE,
            detail=get_search_characters_length_must_be_greater_than_three(length=SEARCH_CHARACTERS_MIN_LENGTH)
        )

    tags = await tag_service.search_tags(db=db, characters=characters, skip=skip, limit=limit)
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
            status_code=TAG_ALREADY_EXISTS_STATUS_CODE,
            detail=get_tag_already_exists_detail_message(tag.name, ObjectType.TAG)
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
            status_code=OBJECT_CANNOT_BE_FOUND_STATUS_CODE,
            detail=get_object_cannot_be_found_detail_message(tag_slug, ObjectType.TAG)
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
            status_code=OBJECT_CANNOT_BE_FOUND_STATUS_CODE,
            detail=get_object_cannot_be_found_detail_message(tag_slug, ObjectType.TAG)
        )

    ok = await tag_service.delete_tag_by_slug(db=db, tag_slug=tag_slug)

    if ok is False:
        raise _fastapi.HTTPException(
            status_code=OBJECT_CANNOT_BE_DELETED_STATUS_CODE,
            detail=get_object_cannot_be_deleted_detail_message(tag_slug, ObjectType.TAG)
        )

    return {
        f"{SUCCESSFUL_DELETION_MESSAGE_KEY}": f"{SUCCESSFUL_DELETION_MESSAGE_VALUE_FOR_TAG}"
    }
