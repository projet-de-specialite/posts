import os
from typing import Union
from uuid import UUID

import fastapi as _fastapi
import sqlalchemy.orm as _orm

import project.src.app.schemas as _schemas
import project.src.app.services.post as post_service
from project.src.app.app_enums.likePostActionEnum import LikePostActionEnum
from project.src.app.routes.shared_constants_and_methods import (
    SUCCESSFUL_DELETION_MESSAGE_KEY,
    SUCCESSFUL_DELETION_MESSAGE_VALUE_FOR_POST, get_forbidden_request_detail_message, FORBIDDEN_REQUEST_STATUS_CODE,
    OBJECT_CANNOT_BE_FOUND_STATUS_CODE, get_object_cannot_be_found_detail_message, ObjectType,
    OBJECT_CANNOT_BE_DELETED_STATUS_CODE, get_object_cannot_be_deleted_detail_message,
    get_create_post_owner_id_greater_than_zero_error_detail_message, VALUE_LENGTH_ERROR_STATUS_CODE)
from project.src.config.db.database import SessionLocal

posts_router = _fastapi.APIRouter(
    prefix="/api/v1/posts",
    tags=["posts"],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@posts_router.get("/", response_model=list[_schemas.Post])
async def fetch_posts(
        owners_ids: Union[list[int], None] = _fastapi.Query(default=None, alias="owners"),
        tags_slug: Union[list[str], None] = _fastapi.Query(default=None, alias="tags"),
        skip: int = post_service.SKIP_DEFAULT_NUMBER,
        limit: int = post_service.LIMIT_DEFAULT_NUMBER,
        db: _orm.Session = _fastapi.Depends(get_db)
):
    """
    Fetches all the posts \n
    You can provide: \n
    - **the owners id** \n
    - **the tags** \n
    - **the skip value** \n
    - **the limit value** \n
    \f
    :param limit: Query param 'limit' \n
    :param skip: Query param 'skip' \n
    :param db: A database session \n
    :param owners_ids: If set, fetches all the posts of the users corresponding to the given users ids \n
    :param tags_slug: If set, fetches all the posts with the given tag \n
    :return: All the posts in the database
    """
    posts = await post_service.get_posts(
        db=db,
        owners_ids=owners_ids,
        tags_slug=tags_slug,
        skip=skip,
        limit=limit
    )
    return posts


@posts_router.get("/latest/", response_model=list[_schemas.Post])
async def fetch_latest_posts(
        owners_ids: Union[list[int], None] = _fastapi.Query(default=None, alias="owners"),
        tags_slug: Union[list[str], None] = _fastapi.Query(default=None, alias="tags"),
        skip: int = post_service.SKIP_DEFAULT_NUMBER,
        limit: int = post_service.LIMIT_DEFAULT_NUMBER,
        db: _orm.Session = _fastapi.Depends(get_db)
):
    """
    Fetches all the latest posts - post sorted by creation date (desc) \n
    You can provide: \n
    - **the owners id** \n
    - **the tags** \n
    - **the skip value** \n
    - **the limit value** \n
    \f
    :param limit: Query param 'limit' \n
    :param skip: Query param 'skip' \n
    :param db: A database session \n
    :param owners_ids: If set, fetches all the posts of the users corresponding to the given users ids \n
    :param tags_slug: If set, fetches all the posts with the given tag \n
    :return: All the posts in the database
    """
    posts = await post_service.get_posts(
        db=db,
        owners_ids=owners_ids,
        tags_slug=tags_slug,
        skip=skip,
        limit=limit,
        latest=True
    )
    return posts


@posts_router.get("/{post_id}", response_model=_schemas.Post)
async def get_post(post_id: UUID, db: _orm.Session = _fastapi.Depends(get_db)):
    """
    Gets a single post by is id \n
    You must provide: \n
    - **the post id** \n
    \f
    :param db: A database session \n
    :param post_id: The post id to get \n
    :return: The post with the given id
    """
    db_post = await post_service.get_post_by_id(db=db, post_id=post_id)

    if db_post is None:
        raise _fastapi.HTTPException(
            status_code=OBJECT_CANNOT_BE_FOUND_STATUS_CODE,
            detail=get_object_cannot_be_found_detail_message(post_id, ObjectType.POST)
        )

    return db_post


@posts_router.post("/new", response_model=_schemas.Post)
async def create_post(
        file: _fastapi.UploadFile,
        caption: str | None = None,
        tags: list[str] | None = [],
        published: bool = False,
        owner_id: int = 1,
        db: _orm.Session = _fastapi.Depends(get_db)
):
    """
    Creates a post \n
    You must provide: \n
    - **the post's information to create** \n
    - **an image** \n
    \f
    :param caption:
    :param tags:
    :param published:
    :param owner_id:
    :param file: \n
    :param db: A database session \n
    # :param post: The post to create - More precisely, all the attributes needed to create a post \n
    :return: The created post
    """
    if owner_id <= 0:
        raise _fastapi.HTTPException(
            status_code=VALUE_LENGTH_ERROR_STATUS_CODE,
            detail=get_create_post_owner_id_greater_than_zero_error_detail_message()
        )

    post_tags = []
    for tag in tags:
        post_tags.append(
            _schemas.TagCreate(
                name=tag
            )
        )

    post = _schemas.PostCreate(
        caption=caption,
        tags=post_tags,
        published=published,
        owner_id=owner_id
    )

    db_post = await post_service.create_post(db=db, post=post, file=file)
    return db_post


@posts_router.get("{post_id}/get-image/")
async def get_upload_file(post_id: UUID, db: _orm.Session = _fastapi.Depends(get_db)):
    db_post = await post_service.get_post_by_id(db=db, post_id=post_id)

    if db_post is None:
        raise _fastapi.HTTPException(
            status_code=OBJECT_CANNOT_BE_FOUND_STATUS_CODE,
            detail=get_object_cannot_be_found_detail_message(post_id, ObjectType.POST)
        )

    filepath = db_post.image
    if os.path.exists(filepath):
        return _fastapi.responses.FileResponse(filepath)
    return {"error": "File not found!"}


@posts_router.put("/{post_id}/comments/add/{comment_id}", response_model=_schemas.Post)
async def add_comment(post_id: UUID, comment_id: int, db: _orm.Session = _fastapi.Depends(get_db)):
    """
    Adds a comment to a post \n
    You must provide: \n
    - **the post id** \n
    - **the comment's id to add** \n
    \f
    :param post_id: The id of the post to add the comment to \n
    :param comment_id: The comment to add \n
    :param db: A database session \n
    :return: The updated post
    """
    db_post = await post_service.get_post_by_id(db=db, post_id=post_id)

    if db_post is None:
        raise _fastapi.HTTPException(
            status_code=OBJECT_CANNOT_BE_FOUND_STATUS_CODE,
            detail=get_object_cannot_be_found_detail_message(post_id, ObjectType.POST)
        )

    return await post_service.add_comment_to_post(db=db, post_id=post_id, comment_id=comment_id)


@posts_router.put("/{post_id}/comments/remove/{comment_id}", response_model=_schemas.Post)
async def remove_comment(post_id: UUID, comment_id: int, db: _orm.Session = _fastapi.Depends(get_db)):
    """
    Removes a comment from a post \n
    You must provide: \n
    - **the post id** \n
    - **the comment's id to remove** \n
    \f
    :param post_id: The id of the post to remove the comment from \n
    :param comment_id: The comment to remove \n
    :param db: A database session \n
    :return: The updated post
    """
    db_post = await post_service.get_post_by_id(db=db, post_id=post_id)

    if db_post is None:
        raise _fastapi.HTTPException(
            status_code=OBJECT_CANNOT_BE_FOUND_STATUS_CODE,
            detail=get_object_cannot_be_found_detail_message(post_id, ObjectType.POST)
        )

    return await post_service.remove_comment_from_post(db=db, post_id=post_id, comment_id=comment_id)


@posts_router.put("/{post_id}/comments/remove-all", response_model=_schemas.Post)
async def remove_all_comments(post_id: UUID, db: _orm.Session = _fastapi.Depends(get_db)):
    """
    Removes all comments from a post \n
    You must provide: \n
    - **the post id** \n
    \f
    :param post_id: The id of the post to remove the comments from \n
    :param db: A database session \n
    :return: The updated post
    """
    db_post = await post_service.get_post_by_id(db=db, post_id=post_id)

    if db_post is None:
        raise _fastapi.HTTPException(
            status_code=OBJECT_CANNOT_BE_FOUND_STATUS_CODE,
            detail=get_object_cannot_be_found_detail_message(post_id, ObjectType.POST)
        )

    return await post_service.remove_all_comments_from_post(db=db, post_id=post_id)


@posts_router.put("/{post_id}", response_model=_schemas.Post)
async def like_or_unlike_post(
        post_id: UUID,
        like_action: LikePostActionEnum = _fastapi.Query(default=..., title="Like/Dislike a post"),
        db: _orm.Session = _fastapi.Depends(get_db)):
    """
    Likes or dislikes a post \n
    You must provide: \n
    - **the post id** \n
    - **the action to perform: like OR unlike** \n
    \f
    :param like_action: Defines the action of liking or disliking a post \n
    :param post_id: The id of the post to remove the comments from \n
    :param db: A database session \n
    :return: The updated post
    """
    db_post = await post_service.get_post_by_id(db=db, post_id=post_id)

    if db_post is None:
        raise _fastapi.HTTPException(
            status_code=OBJECT_CANNOT_BE_FOUND_STATUS_CODE,
            detail=get_object_cannot_be_found_detail_message(post_id, ObjectType.POST)
        )

    if like_action.value == LikePostActionEnum.UNLIKE.value:
        if db_post.likes <= 0:
            return db_post

    return await post_service.like_unlike_post(db=db, post_id=post_id, like_action=like_action)


@posts_router.put("/update/{post_id}", response_model=_schemas.Post)
async def update_post(post_id: UUID, upd_post: _schemas.PostUpdate, user_id: int,
                      db: _orm.Session = _fastapi.Depends(get_db)):
    """
    Updates an exiting post \n
    You must provide: \n
    - **the post id** \n
    - **the modifications to perform on the post (via JSON)** \n
    - **the id of the user performing the request** \n
    \f
    :param db: A database session \n
    :param post_id: The post id \n
    :param upd_post: The data to update in the post \n
    :param user_id: The user (trying to modify the post) id \n
    :return: The updated post
    """
    db_post = await post_service.get_post_by_id(db=db, post_id=post_id)

    if db_post is None:
        raise _fastapi.HTTPException(
            status_code=OBJECT_CANNOT_BE_FOUND_STATUS_CODE,
            detail=get_object_cannot_be_found_detail_message(post_id, ObjectType.POST)
        )

    if db_post.owner_id != user_id:
        raise _fastapi.HTTPException(
            status_code=FORBIDDEN_REQUEST_STATUS_CODE,
            detail=get_forbidden_request_detail_message()
        )

    if db_post.published:
        if (upd_post.caption is None) & (upd_post.tags is None):
            return db_post

    return await post_service.update_post(db=db, post_id=post_id, upd_post=upd_post)


@posts_router.delete("/delete/{post_id}")
async def delete_post(post_id: UUID, user_id: int, db: _orm.Session = _fastapi.Depends(get_db)):
    """
    Deletes a post \n
    You must provide: \n
    - **the post id** \n
    - **the id of the user performing the request** \n
    \f
    :param db: A database session \n
    :param post_id: The post id to delete \n
    :param user_id: The user (trying to modify the post) id \n
    :return: A success message
    """
    db_post = await post_service.get_post_by_id(db=db, post_id=post_id)
    # delete image from bucket

    if db_post is None:
        raise _fastapi.HTTPException(
            status_code=OBJECT_CANNOT_BE_FOUND_STATUS_CODE,
            detail=get_object_cannot_be_found_detail_message(post_id, ObjectType.POST)
        )

    if db_post.owner_id != user_id:
        raise _fastapi.HTTPException(
            status_code=FORBIDDEN_REQUEST_STATUS_CODE,
            detail=get_forbidden_request_detail_message()
        )

    filepath = db_post.image
    ok = await post_service.delete_post(db=db, post_id=post_id)

    if ok is False:
        raise _fastapi.HTTPException(
            status_code=OBJECT_CANNOT_BE_DELETED_STATUS_CODE,
            detail=get_object_cannot_be_deleted_detail_message(post_id, ObjectType.POST)
        )

    # Delete image file
    if os.path.exists(filepath):
        os.remove(filepath)

    return {
        f"{SUCCESSFUL_DELETION_MESSAGE_KEY}": f"{SUCCESSFUL_DELETION_MESSAGE_VALUE_FOR_POST}"
    }
