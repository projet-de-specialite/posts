import datetime as _datetime
import sqlalchemy.orm as _orm

from project.src.app import models as _models
from project.src.app import schemas as _schemas


async def get_tags(db: _orm.Session, skip: int = 0, limit: int = 100):
    """
    Gets all the tags \n
    :param db: A database session \n
    :param skip: Query param 'skip' \n
    :param limit: Query param 'limit'
    :return: A list of tags
    """
    return db.query(_models.Tag)\
        .options(_orm.joinedload(_models.Tag.posts))\
        .offset(skip).limit(limit).all()


async def get_tag_by_slug(db: _orm.Session, tag_slug: str):
    """
    Gets a tag \n
    :param db: A database session \n
    :param tag_slug: The slug of the [wanted] tag \n
    :return: The found tag
    """
    tag_slug = tag_slug.lower()
    return db.query(_models.Tag)\
        .options(_orm.joinedload(_models.Tag.posts))\
        .filter(_models.Tag.slug == tag_slug).first()


async def create_tag(db: _orm.Session, tag: _schemas.TagCreate):
    """
    Creates a tag \n
    :param db: A database session \n
    :param tag: The data to create the tag \n
    :return: The created tag
    """
    db_tag = _models.Tag(
        **tag.dict(),
        slug=tag.name.lower()
    )
    db_tag.created_on = _datetime.datetime.now()

    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


async def create_tag_from_post(db: _orm.Session, tags: list[_schemas.TagCreate]):
    """
    Creates a tag while creating a post \n
    :param db: A database session \n
    :param tags: The list of tags \n
    :return: True 
    """
    rsl_tags = []
    for tag in tags:
        db_tag = await get_tag_by_slug(db=db, tag_slug=tag.name.lower())
        if db_tag is None:
            rsl_tag = await create_tag(db=db, tag=tag)
            rsl_tags.append(rsl_tag)
        else:
            rsl_tags.append(db_tag)

    return rsl_tags


async def delete_tag_by_slug(db: _orm.Session, tag_slug: str):
    """
    Deletes a tag - Used only for the tests \n
    :param db: A database session \n
    :param tag_slug: The tag's slug \n
    :return: True
    """
    try:
        tag_slug = tag_slug.lower()
        db_tag = await get_tag_by_slug(db=db, tag_slug=tag_slug)
        db.delete(db_tag)
        db.commit()
        return True
    except:
        return False
