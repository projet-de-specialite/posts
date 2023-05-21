from typing import Union
from uuid import UUID

import fastapi as _fastapi
import sqlalchemy.orm as _orm

import project.src.app.schemas as _schemas
import project.src.app.services.post as post_service
from project.src.app.app_enums.likePostActionEnum import LikePostActionEnum
from project.src.app.routes.shared_constants_and_methods import (
    SUCCESSFUL_DELETION_MESSAGE_KEY,
    SUCCESSFUL_DELETION_MESSAGE_VALUE_FOR_POST)
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
    skip: int = 0,
    limit: int = 100,
    db: _orm.Session = _fastapi.Depends(get_db)
):
    """
    Fetches all the posts \n
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
    skip: int = 0,
    limit: int = 100,
    db: _orm.Session = _fastapi.Depends(get_db)
):
    """
    Fetches all the latest posts - post sorted by creation date (desc) \n
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
    :param db: A database session \n
    :param post_id: The post id to get \n
    :return: The post with the given id
    """
    db_post = await post_service.get_post_by_id(db=db, post_id=post_id)

    if db_post is None:
        raise _fastapi.HTTPException(
            status_code=404,
            detail=f"The post with id: {post_id} cannot be found!"
        )

    return db_post


@posts_router.post("/new", response_model=_schemas.Post)
async def create_post(post: _schemas.PostCreate, db: _orm.Session = _fastapi.Depends(get_db)):
    """
    Creates a post \n
    :param db: A database session \n
    :param post: The post to create - More precisely, all the attributes needed to create a post \n
    :return: The created post
    """
    # add image to bucket
    # post.image = ""
    db_post = await post_service.create_post(db=db, post=post)
    return db_post


@posts_router.put("/{post_id}/comments/add/{comment_id}", response_model=_schemas.Post)
async def add_comment(post_id: UUID, comment_id: int, db: _orm.Session = _fastapi.Depends(get_db)):
    """
    Adds a comment to a post \n
    :param post_id: The id of the post to add the comment to \n
    :param comment_id: The comment to add \n
    :param db: A database session \n
    :return: The updated post
    """
    db_post = await post_service.get_post_by_id(db=db, post_id=post_id)

    if db_post is None:
        raise _fastapi.HTTPException(
            status_code=404,
            detail=f"The post with id: {post_id} cannot be found!"
        )

    return await post_service.add_comment_to_post(db=db, post_id=post_id, comment_id=comment_id)


@posts_router.put("/{post_id}/comments/remove/{comment_id}", response_model=_schemas.Post)
async def remove_comment(post_id: UUID, comment_id: int, db: _orm.Session = _fastapi.Depends(get_db)):
    """
    Removes a comment from a post \n
    :param post_id: The id of the post to remove the comment from \n
    :param comment_id: The comment to remove \n
    :param db: A database session \n
    :return: The updated post
    """
    db_post = await post_service.get_post_by_id(db=db, post_id=post_id)

    if db_post is None:
        raise _fastapi.HTTPException(
            status_code=404,
            detail=f"The post with id: {post_id} cannot be found!"
        )

    return await post_service.remove_comment_from_post(db=db, post_id=post_id, comment_id=comment_id)


@posts_router.put("/{post_id}/comments/remove-all", response_model=_schemas.Post)
async def remove_all_comments(post_id: UUID, db: _orm.Session = _fastapi.Depends(get_db)):
    """
    Removes all comments from a post \n
    :param post_id: The id of the post to remove the comments from \n
    :param db: A database session \n
    :return: The updated post
    """
    db_post = await post_service.get_post_by_id(db=db, post_id=post_id)

    if db_post is None:
        raise _fastapi.HTTPException(
            status_code=404,
            detail=f"The post with id: {post_id} cannot be found!"
        )

    return await post_service.remove_all_comments_from_post(db=db, post_id=post_id)


@posts_router.put("/{post_id}", response_model=_schemas.Post)
async def like_or_unlike_post(
        post_id: UUID,
        like_action: LikePostActionEnum = _fastapi.Query(default=..., title="Like/Dislike a post"),
        db: _orm.Session = _fastapi.Depends(get_db)):
    """
    Likes or dislikes a post \n
    :param like_action: Defines the action of liking or disliking a post \n
    :param post_id: The id of the post to remove the comments from \n
    :param db: A database session \n
    :return: The updated post
    """
    db_post = await post_service.get_post_by_id(db=db, post_id=post_id)

    if db_post is None:
        raise _fastapi.HTTPException(
            status_code=404,
            detail=f"The post with id: {post_id} cannot be found!"
        )
    
    if like_action.value == LikePostActionEnum.UNLIKE.value:
        if db_post.likes <= 0:
            return db_post

    return await post_service.like_unlike_post(db=db, post_id=post_id, like_action=like_action)


@posts_router.put("/update/{post_id}", response_model=_schemas.Post)
async def update_post(post_id: UUID, upd_post: _schemas.PostUpdate, db: _orm.Session = _fastapi.Depends(get_db)):
    """
    Updates an exiting post \n
    :param db: A database session \n
    :param post_id: The post id \n
    :param upd_post: The data to update in the post \n
    :return: The updated post
    """
    db_post = await post_service.get_post_by_id(db=db, post_id=post_id)

    if db_post is None:
        raise _fastapi.HTTPException(
            status_code=404,
            detail=f"The post with id: {post_id} cannot be found!"
        )
    
    if db_post.published:
        if (upd_post.caption is None) & (upd_post.tags is None):
            return db_post

    return await post_service.update_post(db=db, post_id=post_id, upd_post=upd_post)


@posts_router.delete("/delete/{post_id}")
async def delete_post(post_id: UUID, db: _orm.Session = _fastapi.Depends(get_db)):
    """
    Deletes a post \n
    :param db: A database session \n
    :param post_id: The post id to delete \n
    :return: A success message
    """
    db_post = await post_service.get_post_by_id(db=db, post_id=post_id)
    # delete image from bucket

    if db_post is None:
        raise _fastapi.HTTPException(
            status_code=404,
            detail=f"The post with id: {post_id} cannot be found!"
        )

    ok = await post_service.delete_post(db=db, post_id=post_id)

    if ok is False:
        raise _fastapi.HTTPException(
            status_code=400,
            detail=f"Could not delete the post with id: {post_id}!"
        )

    return {
        f"{ SUCCESSFUL_DELETION_MESSAGE_KEY }": f"{ SUCCESSFUL_DELETION_MESSAGE_VALUE_FOR_POST }"
    }
