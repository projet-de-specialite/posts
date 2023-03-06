import project.src.config.db.database as _database
import project.src.app.models.post as _post
import project.src.app.models.tag as _tag


def _add_tables_to_picshare_database():
    return _database.Base.metadata.create_all(bind=_database.engine)

