import os

import sqlalchemy as _sql
import sqlalchemy.orm as _orm
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

metadata = _sql.MetaData()

engine = _sql.create_engine(DATABASE_URL)
SessionLocal = _orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = _orm.declarative_base()


# The (association) table linking posts and tags - post_tag_linker
post_tag_linker = _sql.Table(
    "post_tag_linker", Base.metadata,
    _sql.Column("post_id", _sql.Uuid, _sql.ForeignKey("posts.id"), primary_key=True),
    _sql.Column("tag_id", _sql.Uuid, _sql.ForeignKey("tags.id"), primary_key=True)
)
