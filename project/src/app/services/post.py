import datetime as _datetime
import os
import shutil
import uuid
from http import HTTPStatus
from pathlib import Path
from typing import Optional
from uuid import UUID

import sqlalchemy as _sql
import sqlalchemy.orm as _orm
from dotenv import load_dotenv
from fastapi import UploadFile, HTTPException

import project.src.app.services.tag as _tag_service
from project.src.app import models as _models
from project.src.app import schemas as _schemas
from project.src.app.app_enums.likePostActionEnum import LikePostActionEnum

load_dotenv()
SKIP_DEFAULT_NUMBER = 0
LIMIT_DEFAULT_NUMBER = 100
LATEST_DEFAULT_VALUE = False


async def get_posts(db: _orm.Session, owners_ids: list[int] | None, tags_slug: list[str] | None,
                    skip: int = SKIP_DEFAULT_NUMBER, limit: int = LIMIT_DEFAULT_NUMBER,
                    latest: Optional[bool] = LATEST_DEFAULT_VALUE):
    """
    Gets all the posts \n
    :param owners_ids:
    :param db: A database session \n
    :param owners_ids: The [posts] owners ids \n
    :param tags_slug: The [posts] tags \n
    :param skip: Query param 'skip' \n
    :param limit: Query param 'limit' \n
    :param latest: Defines whether the request concerns the latest posts or not \n
    :return: A list of posts
    """
    if (owners_ids is not None) & (tags_slug is not None):
        return await get_posts_by_owners_and_tags(db=db, owners_ids=owners_ids,
                                                  tags_slug=tags_slug, skip=skip, limit=limit, latest=latest)
    else:
        if owners_ids is not None:
            return await get_posts_by_owners(db=db, owners_ids=owners_ids,
                                             skip=skip, limit=limit, latest=latest)
        if tags_slug is not None:
            return await get_posts_by_tags(db=db, tags_slug=tags_slug,
                                           skip=skip, limit=limit, latest=latest)

    if latest is True:
        return db.query(_models.Post) \
            .options(_orm.joinedload(_models.Post.tags)) \
            .order_by(_models.Post.created_on.desc()) \
            .offset(skip).limit(limit).all()

    return db.query(_models.Post) \
        .options(_orm.joinedload(_models.Post.tags)) \
        .offset(skip).limit(limit).all()


async def get_posts_by_owners_and_tags(db: _orm.Session, owners_ids: list[int],
                                       tags_slug: list[str], skip: int = SKIP_DEFAULT_NUMBER,
                                       limit: int = LIMIT_DEFAULT_NUMBER,
                                       latest: Optional[bool] = LATEST_DEFAULT_VALUE):
    """
    Gets all the posts owned by each listed owner and with all the specified tags \n
    :param latest:
    :param db: A database session \n
    :param owners_ids: The [posts] owners ids \n
    :param tags_slug: The [posts] tags \n
    :param skip: Query param 'skip' \n
    :param limit: Query param 'limit' \n
    :return: A list of posts
    """
    posts_by_tags = await get_posts_by_tags(db=db, tags_slug=tags_slug,
                                            skip=skip, limit=limit, latest=latest)
    posts_by_owners = await get_posts_by_owners(db=db, owners_ids=owners_ids,
                                                skip=skip, limit=limit, latest=latest)

    if len(posts_by_tags) < len(posts_by_owners):
        posts = [p for p in posts_by_tags if p in posts_by_owners]
    else:
        posts = [p for p in posts_by_owners if p in posts_by_tags]

    if latest is True:
        posts.sort(key=lambda x: x.created_on, reverse=True)

    new_posts = posts[skip:limit]

    return new_posts


async def get_posts_by_tags(db: _orm.Session, tags_slug: list[str],
                            skip: Optional[int] = SKIP_DEFAULT_NUMBER, limit: Optional[int] = LIMIT_DEFAULT_NUMBER,
                            latest: Optional[bool] = LATEST_DEFAULT_VALUE):
    """
    Gets the posts having all the specified tags \n
    :param latest:
    :param limit:
    :param skip:
    :param db: A database session \n
    :param tags_slug: A list of tag slug \n
    :return: A list of posts
    """
    posts = []
    for slug in tags_slug:
        tag = await _tag_service.get_tag_by_slug(db, slug)

        if tag is not None:
            posts_temp = tag.posts
            posts = [p for p in posts_temp if p in posts] if posts != [] else posts_temp

    if latest is True:
        posts.sort(key=lambda x: x.created_on, reverse=True)

    new_posts = posts[skip:limit]

    return new_posts


async def get_posts_by_owners(db: _orm.Session, owners_ids: list[int],
                              skip: Optional[int] = SKIP_DEFAULT_NUMBER, limit: Optional[int] = LIMIT_DEFAULT_NUMBER,
                              latest: Optional[bool] = LATEST_DEFAULT_VALUE):
    """
    Gets the posts having all the specified tags \n
    :param owners_ids:
    :param db: A database session \n
    :param latest:
    :param limit:
    :param skip:
    :return: A list of posts
    """
    posts = []
    owners_ids = set(owners_ids)
    for owner_id in owners_ids:
        posts_by_owner = await get_posts_by_owner(db=db, owner_id=owner_id, skip=skip,
                                                  limit=limit, latest=latest)
        posts += posts_by_owner

    if latest is True:
        posts.sort(key=lambda x: x.created_on, reverse=True)

    new_posts = posts[skip:limit]

    return new_posts


async def get_posts_by_owner(db: _orm.Session, owner_id: int, skip: int = SKIP_DEFAULT_NUMBER,
                             limit: int = LIMIT_DEFAULT_NUMBER, latest: Optional[bool] = LATEST_DEFAULT_VALUE):
    """
    Gets all the posts owned by the user [with user_id = owner_id] \n
    :param latest:
    :param db: A database session \n
    :param owner_id: The [posts] owner id \n
    :param skip: Query param 'skip' \n
    :param limit: Query param 'limit' \n
    :return: A list of posts
    """
    if latest is True:
        return db.query(_models.Post) \
            .options(_orm.joinedload(_models.Post.tags)) \
            .filter(_models.Post.owner_id == owner_id) \
            .order_by(_models.Post.created_on.desc()) \
            .offset(skip).limit(limit).all()

    return db.query(_models.Post) \
        .options(_orm.joinedload(_models.Post.tags)) \
        .filter(_models.Post.owner_id == owner_id) \
        .offset(skip).limit(limit).all()


async def get_post_by_id(db: _orm.Session, post_id: UUID):
    """
    Gets the post with id = post_id \n
    :param db: A database session \n
    :param post_id: The [wanted] post id \n
    :return: A post
    """
    return db.query(_models.Post) \
        .options(_orm.joinedload(_models.Post.tags)) \
        .filter(_models.Post.id == post_id).first()


async def save_upload_file(upload_file: UploadFile, destination: Path) -> None:
    """
    Save file to images directory \n
    :param upload_file: \n
    :param destination: \n
    :return:
    """
    try:
        upload_file.file.seek(0)
        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    except Exception as err:
        raise HTTPException(detail=f'{err} encountered while uploading {upload_file.filename}',
                            status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
    finally:
        upload_file.file.close()


async def create_post(db: _orm.Session, post: _schemas.PostCreate, file: UploadFile):
    """
    Creates a post \n
    :param file: \n
    :param db: A database session \n
    :param post: All the needed data to create a post \n
    :return: The created post
    """
    db_tags = []
    # check if there are new tags - if so, create them 
    if post.tags:
        db_tags = await _tag_service.create_tag_from_post(db=db, tags=post.tags)

    db_post = _models.Post(
        image="",
        caption=post.caption,
        published=post.published,
        owner_id=post.owner_id,
        tags=db_tags
    )
    now_datetime = _datetime.datetime.now()
    db_post.published_on = now_datetime if post.published else _schemas.DEFAULT_DATETIME
    db_post.created_on = now_datetime
    db_post.updated_on = now_datetime

    db.add(db_post)
    db.commit()

    post_id = db_post.id
    destination = f"{os.getenv('IMAGES_DIRECTORY_NAME')}/{post_id}_{file.filename}"

    await save_upload_file(upload_file=file, destination=Path(destination))

    db.execute(
        _sql.update(_models.Post).where(_models.Post.id == post_id)
        .values(image=destination)
    )
    db.commit()
    db.refresh(db_post)

    return db_post


async def like_unlike_post(db: _orm.Session, post_id: uuid.UUID, like_action: LikePostActionEnum):
    """
    Publishes - sets the 'published' attribute to True - a post \n
    :param like_action: Defines whether it's the action of liking or disliking a post \n
    :param db: A database session \n
    :param post_id: The id of the post to publish \n
    :return: The updated post
    """
    db.execute(
        _sql.update(_models.Post).where(_models.Post.id == post_id)
        .values(likes=_models.Post.likes + 1 if (like_action.value == LikePostActionEnum.LIKE.value) else _models.Post.likes - 1)
    )

    db.commit()
    return await get_post_by_id(db=db, post_id=post_id)


async def update_post(db: _orm.Session, post_id: uuid.UUID, upd_post: _schemas.PostUpdate) -> _schemas.Post:
    """
    Updates a post \n
    :param db: A database session \n
    :param post_id: The post id to update \n
    :param upd_post: The post's new data \n
    :return: The updated post
    """
    now_datetime = _datetime.datetime.now()
    db_post = await get_post_by_id(db=db, post_id=post_id)
    has_been_updated = False

    if upd_post.caption is not None:
        db_post.caption = upd_post.caption
        has_been_updated = True

    if upd_post.tags is not None:
        db_tags = await _tag_service.create_tag_from_post(db=db, tags=upd_post.tags)
        db_post.tags = [] if db_tags is None else db_tags
        has_been_updated = True

    if db_post.published is False & upd_post.published:
        if upd_post.published is True:
            db_post.published = True
            db_post.published_on = now_datetime
            has_been_updated = True

    db.execute(
        _sql.update(_models.Post).where(_models.Post.id == post_id)
        .values(updated_on=_models.Post.updated_on if has_been_updated is False else now_datetime)
    )

    db.commit()
    return await get_post_by_id(db=db, post_id=post_id)


async def delete_post(db: _orm.Session, post_id: uuid.UUID):
    """
    Deletes - puts the 'visible' attribute to false - a post \n
    :param db: A database session \n
    :param post_id: The post id to delete \n
    :return: True if deleted
    """
    db_post = await get_post_by_id(db=db, post_id=post_id)
    db.delete(db_post)
    db.commit()
    return True
