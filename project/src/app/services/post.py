import datetime as _datetime
import uuid
from typing import Optional
from uuid import UUID

import sqlalchemy as _sql
import sqlalchemy.orm as _orm

import project.src.app.services.tag as _tag_service
from project.src.app import models as _models
from project.src.app import schemas as _schemas
from project.src.app.app_enums.likePostActionEnum import LikePostActionEnum


async def get_posts(db: _orm.Session, owners_ids: list[str] | None, tags_slug: list[str] | None,
                    skip: int = 0, limit: int = 100, latest: Optional[bool] = False):
    """
    Gets all the posts \n
    :param db: A database session \n
    :param owner_id: The [posts] owners ids \n
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
        return db.query(_models.Post)\
            .options(_orm.joinedload(_models.Post.tags))\
            .order_by(_models.Post.created_on.desc())\
            .offset(skip).limit(limit).all()

    return db.query(_models.Post)\
        .options(_orm.joinedload(_models.Post.tags))\
        .offset(skip).limit(limit).all()


async def get_posts_by_owners_and_tags(db: _orm.Session, owners_ids: list[int], 
            tags_slug: list[str], skip: int, limit: int,
                latest: Optional[bool]):
    """
    Gets all the posts owned by each listed owner and with all the specified tags \n
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

    new_posts = posts
    if (limit is not None & skip is not None):
        new_posts = posts[skip:limit]

    return new_posts


async def get_posts_by_tags(db: _orm.Session, tags_slug: list[str],
                    skip: Optional[int], limit: Optional[int], latest: Optional[bool]):
    """
    Gets the posts having all the specified tags \n
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

    new_posts = posts
    if (limit is not None & skip is not None):
        new_posts = posts[skip:limit]

    return new_posts


async def get_posts_by_owners(db: _orm.Session, owners_ids: list[int],
                    skip: Optional[int], limit: Optional[int], latest: Optional[bool]):
    """
    Gets the posts having all the specified tags \n
    :param db: A database session \n
    :param tags_slug: A list of tag slug \n
    :return: A list of posts
    """
    posts = []
    owners_ids = set(owners_ids)
    for owner_id in owners_ids:
        posts_by_owner = await get_posts_by_owner(db=db, owner_id=owner_id,
                            limit=limit, latest=latest)
        posts += posts_by_owner

    if latest is True:
        posts.sort(key=lambda x: x.created_on, reverse=True)

    new_posts = posts
    if (limit is not None & skip is not None):
        new_posts = posts[skip:limit]

    return new_posts


async def get_posts_by_owner(db: _orm.Session, owner_id: int,
            limit: int = 100, latest: Optional[bool] = False):
    """
    Gets all the posts owned by the user [with user.id = owner_id] \n
    :param db: A database session \n
    :param owner_id: The [posts] owner id \n
    :param skip: Query param 'skip' \n
    :param limit: Query param 'limit' \n
    :return: A list of posts
    """
    if latest is True:
        return db.query(_models.Post)\
            .options(_orm.joinedload(_models.Post.tags))\
            .filter(_models.Post.owner_id == owner_id)\
            .order_by(_models.Post.created_on.desc())\
            .limit(limit).all()

    return db.query(_models.Post)\
        .options(_orm.joinedload(_models.Post.tags))\
        .filter(_models.Post.owner_id == owner_id)\
        .limit(limit).all()


async def get_post_by_id(db: _orm.Session, post_id: UUID):
    """
    Gets the post with id = post_id \n
    :param db: A database session \n
    :param post_id: The [wanted] post id \n
    :return: A post
    """
    return db.query(_models.Post)\
        .options(_orm.joinedload(_models.Post.tags))\
        .filter(_models.Post.id == post_id).first()


async def create_post(db: _orm.Session, post: _schemas.PostCreate):
    """
    Creates a post \n
    :param db: A database session \n
    :param post: All the needed data to create a post \n
    :return: The created post
    """
    # check if there are new tags - if so, create them 
    if post.tags != []:
        db_tags = await _tag_service.create_tag_from_post(db=db, tags=post.tags)

    db_post = _models.Post(
        image=post.image,
        caption=post.caption,
        published=post.published,
        owner_id=post.owner_id,
        tags=[] if db_tags is None else db_tags,
        comments=[]
    )
    now_datetime = _datetime.datetime.now()
    db_post.published_on = now_datetime if post.published else _schemas.DEFAULT_DATETIME
    db_post.created_on = now_datetime
    db_post.updated_on = now_datetime

    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


async def add_comment_to_post(db: _orm.Session, post_id: uuid.UUID, comment_id: int):
    """
    Adds a comment to a post \n
    :param post_id: The id of the post to add the comment to \n
    :param comment_id: The comment to add \n
    :param db: A database session \n
    :return: The updated post
    """
    ct_col = db.execute(_sql.select(_models.Post.comments).where(_models.Post.id == post_id)).all()

    db.execute(
        _sql.update(_models.Post).where((_models.Post.id == post_id) & (comment_id not in ct_col[0][0]))
        .values(comments=_models.Post.comments + [comment_id], updated_on=_datetime.datetime.now())
    )

    db.commit()
    return await get_post_by_id(db=db, post_id=post_id)


async def remove_comment_from_post(db: _orm.Session, post_id: uuid.UUID, comment_id: int):
    """
    Removes a comment from a post \n
    :param post_id: The id of the post to remove the comment from \n
    :param comment_id: The comment to remove \n
    :param db: A database session \n
    :return: The updated post
    """
    ct_col = db.execute(_sql.select(_models.Post.comments).where(_models.Post.id == post_id)).all()
    ct = [elem for elem in ct_col[0][0] if elem != comment_id]

    db.execute(
        _sql.update(_models.Post).where((_models.Post.id == post_id) & (comment_id in ct_col[0][0]))
        .values(comments=ct, updated_on=_datetime.datetime.now())
    )

    db.commit()
    return await get_post_by_id(db=db, post_id=post_id)


async def remove_all_comments_from_post(db: _orm.Session, post_id: uuid.UUID):
    """
    Removes all comments from a post \n
    :param post_id: The id of the post to remove the comments from \n
    :param db: A database session \n
    :return: The updated post
    """
    db.execute(
        _sql.update(_models.Post).where(_models.Post.id == post_id)
        .values(comments=[], updated_on=_datetime.datetime.now())
    )

    db.commit()
    return await get_post_by_id(db=db, post_id=post_id)


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
        .values(likes=_models.Post.likes + 1 if (like_action.value == LikePostActionEnum.LIKE.value)
                else _models.Post.likes - 1)
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
