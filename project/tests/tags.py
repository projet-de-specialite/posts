import os

import fastapi.testclient as _fastapi_testclient
import sqlalchemy as _sql
import sqlalchemy.orm as _orm
from dotenv import load_dotenv

import project.src.config.db.database as _database
from project.src.app.main import app
from project.src.app.routes.important_constants import (
    SUCCESSFUL_DELETION_MESSAGE_KEY, SUCCESSFUL_DELETION_MESSAGE_VALUE_FOR_TAG)
from project.src.app.routes.tags import get_db, tags_router

load_dotenv()

TEST_DATABASE_URL = os.getenv("DATABASE_TEST_URL")

engine = _sql.create_engine(TEST_DATABASE_URL)

TestingSessionLocal = _orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

_database.Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
tags_client = _fastapi_testclient.TestClient(app)

test_tag_id = ""
test_tag_slug = "teddy bear"
test_tag_name = "Teddy Bear"


def test_fetch_tags():
    response = tags_client.get(f"{tags_router.prefix}/")
    assert response.status_code == 200, response.text
    data = response.json()
    print(data)


def test_create_tag_should_succeed():
    global test_tag_id
    response = tags_client.post(
        f"{tags_router.prefix}/new",
        json={"name": test_tag_name},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == test_tag_name, f"Should be '{test_tag_slug}'!"
    assert "id" in data
    assert "slug" in data
    assert data["slug"] == test_tag_slug
    test_tag_id = data["id"]


def test_get_tag_should_succeed():
    response = tags_client.get(f"{tags_router.prefix}/{test_tag_slug}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["slug"] == test_tag_slug, f"Should be '{test_tag_slug}'!"
    assert data["id"] == test_tag_id, f"Should be '{test_tag_id}'!"


def test_get_tag_should_fail():
    tag_slug = "lolita"
    response = tags_client.get(f"{tags_router.prefix}/{tag_slug}")
    assert response.status_code == 404, response.text
    assert response.json() == {"detail": f"The tag with slug: {tag_slug} cannot be found!"}


def test_delete_tag_should_succeed():
    # Delete the tag
    response = tags_client.delete(f"{tags_router.prefix}/delete/{test_tag_slug}")
    data = response.json()
    print(data)
    assert data[f"{SUCCESSFUL_DELETION_MESSAGE_KEY}"] == f"{SUCCESSFUL_DELETION_MESSAGE_VALUE_FOR_TAG}", \
        f"Should be '{SUCCESSFUL_DELETION_MESSAGE_VALUE_FOR_TAG}'"

    # Verify that getting the deleted tag doesn't work
    response = tags_client.get(f"{tags_router.prefix}/{test_tag_slug}")
    assert response.status_code == 404, response.text


def test_delete_tag_should_fail():
    tag_slug = "lolita"
    response = tags_client.delete(f"{tags_router.prefix}/delete/{tag_slug}")
    assert response.status_code == 404, response.text
