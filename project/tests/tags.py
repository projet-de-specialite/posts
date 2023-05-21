import os

import fastapi.testclient as _fastapi_testclient
import sqlalchemy as _sql
import sqlalchemy.orm as _orm
from dotenv import load_dotenv

import project.src.config.db.database as _database
from project.src.app.main import app
from project.src.app.routes.shared_constants_and_methods import (
    SUCCESSFUL_DELETION_MESSAGE_KEY, SUCCESSFUL_DELETION_MESSAGE_VALUE_FOR_TAG,
    get_object_cannot_be_found_detail_message, ObjectType, get_tag_already_exists_detail_message,
    get_search_characters_length_must_be_greater_than_three, VALUE_LENGTH_ERROR_STATUS_CODE,
    TAG_ALREADY_EXISTS_STATUS_CODE, OBJECT_CANNOT_BE_FOUND_STATUS_CODE, REQUEST_IS_OK_STATUS_CODE)
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
    assert response.status_code == REQUEST_IS_OK_STATUS_CODE, response.text


def test_search_tags_should_fail():
    characters = "hp"
    response = tags_client.get(f"{tags_router.prefix}/search/{characters}/")
    assert response.status_code == VALUE_LENGTH_ERROR_STATUS_CODE, response.text
    data = response.json()
    assert data["detail"] == get_search_characters_length_must_be_greater_than_three()


def test_create_tag_should_succeed():
    global test_tag_id
    response = tags_client.post(
        f"{tags_router.prefix}/new",
        json={"name": test_tag_name},
    )

    assert response.status_code == REQUEST_IS_OK_STATUS_CODE, response.text
    data = response.json()
    assert data["name"] == test_tag_name, f"Should be '{test_tag_slug}'!"
    assert "id" in data
    assert "slug" in data
    assert data["slug"] == test_tag_slug
    test_tag_id = data["id"]


def test_create_tag_should_fail():
    tag_name = "hp"
    response = tags_client.post(
        f"{tags_router.prefix}/new",
        json={"name": tag_name},
    )

    assert response.status_code == VALUE_LENGTH_ERROR_STATUS_CODE, response.text
    data = response.json()
    detail = data["detail"][0]["msg"]
    assert detail == "ensure this value has at least 3 characters"


def test_create_existing_tag_should_fail():
    response = tags_client.post(
        f"{tags_router.prefix}/new",
        json={"name": test_tag_name},
    )

    assert response.status_code == TAG_ALREADY_EXISTS_STATUS_CODE, response.text
    assert response.json() == {"detail": get_tag_already_exists_detail_message(test_tag_name, ObjectType.TAG)}


def test_search_tags_should_succeed():
    characters = test_tag_slug[:3]
    response = tags_client.get(f"{tags_router.prefix}/search/{characters}/")
    assert response.status_code == REQUEST_IS_OK_STATUS_CODE, response.text


def test_get_tag_should_succeed():
    response = tags_client.get(f"{tags_router.prefix}/{test_tag_slug}")
    assert response.status_code == REQUEST_IS_OK_STATUS_CODE, response.text
    data = response.json()
    assert data["slug"] == test_tag_slug, f"Should be '{test_tag_slug}'!"
    assert data["id"] == test_tag_id, f"Should be '{test_tag_id}'!"


def test_get_tag_should_fail():
    tag_slug = "lolita"
    response = tags_client.get(f"{tags_router.prefix}/{tag_slug}")
    assert response.status_code == OBJECT_CANNOT_BE_FOUND_STATUS_CODE, response.text
    assert response.json() == {"detail": get_object_cannot_be_found_detail_message(tag_slug, ObjectType.TAG)}


def test_delete_tag_should_succeed():
    # Delete the tag
    response = tags_client.delete(f"{tags_router.prefix}/delete/{test_tag_slug}")
    data = response.json()
    print(data)
    assert data[f"{SUCCESSFUL_DELETION_MESSAGE_KEY}"] == f"{SUCCESSFUL_DELETION_MESSAGE_VALUE_FOR_TAG}", \
        f"Should be '{SUCCESSFUL_DELETION_MESSAGE_VALUE_FOR_TAG}'"

    # Verify that getting the deleted tag doesn't work
    response = tags_client.get(f"{tags_router.prefix}/{test_tag_slug}")
    assert response.status_code == OBJECT_CANNOT_BE_FOUND_STATUS_CODE, response.text


def test_delete_tag_should_fail():
    tag_slug = "lolita"
    response = tags_client.delete(f"{tags_router.prefix}/delete/{tag_slug}")
    assert response.status_code == OBJECT_CANNOT_BE_FOUND_STATUS_CODE, response.text
