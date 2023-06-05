import datetime as _datetime

import sqlalchemy as _sql
import sqlalchemy.orm as _orm

import project.src.config.db.database as _database


class Post(_database.Base):
    """
    The database "posts" table model
    """
    __tablename__ = "posts"
    id = _sql.Column(
        _sql.Uuid,
        primary_key=True,
        index=True,
        server_default=_sql.func.gen_random_uuid()
    )
    image = _sql.Column(_sql.String, nullable=False)
    caption = _sql.Column(_sql.Text, nullable=True, default=None)
    likes = _sql.Column(_sql.Integer, default=0, server_default="0")
    tags = _orm.relationship(
        "Tag",
        secondary=_database.post_tag_linker,
        back_populates="posts"
    )
    published = _sql.Column(
        _sql.Boolean,
        default=True,
        server_default=_sql.sql.false()
    )  # True by default due to draft poss
    published_on = _sql.Column(
        _sql.DateTime,
        default=None,
        nullable=True,
        server_default=None
    )
    owner_id = _sql.Column(_sql.Integer, nullable=False)
    created_on = _sql.Column(
        _sql.DateTime,
        default=_datetime.datetime.now(),
        server_default=_sql.sql.func.now()
    )
    updated_on = _sql.Column(
        _sql.DateTime,
        default=_datetime.datetime.now(),
        server_default=_sql.sql.func.now()
    )
