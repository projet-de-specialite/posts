import datetime as _datetime

import sqlalchemy as _sql
import sqlalchemy.orm as _orm

import project.src.config.db.database as _database


class Tag(_database.Base):
    """
    The database "tags" table model
    """
    __tablename__ = "tags"
    id = _sql.Column(
        _sql.Uuid,
        primary_key=True,
        index=True,
        server_default=_sql.func.gen_random_uuid()
    )
    # The name in lowercase
    slug = _sql.Column(_sql.String, index=True, nullable=False, unique=True)
    name = _sql.Column(_sql.String, index=True, nullable=False, unique=True)
    created_on = _sql.Column(
        _sql.DateTime,
        default=_datetime.datetime.now(),
        server_default=_sql.sql.func.now()
    )
    posts = _orm.relationship(
        "Post",
        secondary=_database.post_tag_linker,
        back_populates="tags"
    )

