import os
import uuid

import sqlalchemy as _sql
import sqlalchemy.orm as _orm
from dotenv import load_dotenv
from fastapi.testclient import TestClient

import project.src.config.db.database as _database
from project.src.app.main import app
from project.src.app.routes.posts import get_db, posts_router
from project.src.app.routes.shared_constants_and_methods import (
    SUCCESSFUL_DELETION_MESSAGE_KEY, SUCCESSFUL_DELETION_MESSAGE_VALUE_FOR_POST, REQUEST_IS_OK_STATUS_CODE,
    POST_ENTITY_BAD_TYPING_ERROR_STATUS_CODE, FORBIDDEN_REQUEST_STATUS_CODE, get_forbidden_request_detail_message,
    OBJECT_CANNOT_BE_FOUND_STATUS_CODE, get_object_cannot_be_found_detail_message, ObjectType,
    VALUE_LENGTH_ERROR_STATUS_CODE)

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
posts_client = TestClient(app)

test_post_id = ""
test_post_image = "post test image"
test_post_caption = "Post test"
test_post_tags = []
test_post_published = False
test_post_owner_id = 1
test_post_comment_id = 1

test_post2_id = ""


def test_fetch_posts_should_succeed():
    response = posts_client.get(f"{posts_router.prefix}/")
    assert response.status_code == REQUEST_IS_OK_STATUS_CODE, response.text
    data = response.json()
    assert data == [], f"Should be [] because there is no posts yet!"

    response = posts_client.get(f"{posts_router.prefix}/?owners=1&owners=3&skip=2")
    assert response.status_code == REQUEST_IS_OK_STATUS_CODE, response.text
    data = response.json()
    assert data == [], f"Should be [] because there is no posts yet!"


def test_fetch_posts_should_fail():
    response = posts_client.get(f"{posts_router.prefix}/?owners=mike")
    assert response.status_code == POST_ENTITY_BAD_TYPING_ERROR_STATUS_CODE, response.text


def test_fetch_latest_posts():
    response = posts_client.get(f"{posts_router.prefix}/latest/")
    assert response.status_code == REQUEST_IS_OK_STATUS_CODE, response.text
    data = response.json()
    assert data == [], f"Should be [] because there is no posts yet!"


def test_create_post_should_succeed():
    global test_post_id
    # files = {"file": open("./test_img/wlpp.jpg", "rb")}
    files = {"file": open("project/tests/test_img/black.png", "rb")}
    os.environ["IMAGES_DIRECTORY_NAME"] = "."

    response = posts_client.post(
        f"{posts_router.prefix}/new?owner_id={test_post_owner_id}&caption={test_post_caption}&tags={test_post_tags}"
        f"&published={test_post_published}",
        files=files
    )

    assert response.status_code == REQUEST_IS_OK_STATUS_CODE, response.text
    data = response.json()
    assert data["caption"] == test_post_caption, f"Should be '{test_post_caption}'!"
    assert data["owner_id"] == test_post_owner_id, f"Should be '{test_post_owner_id}'!"
    assert "id" in data
    assert "image" in data
    assert "tags" in data
    assert "published" in data
    assert "likes" in data
    assert "comments" in data
    assert "created_on" in data
    assert "updated_on" in data
    test_post_id = data["id"]


def test_create_post_should_fail():
    files = {"file": open("project/tests/test_img/wlpp.jpg", "rb")}
    owner_name = "jeremy"
    caption = 45
    tags = "lemon"

    response = posts_client.post(
        f"{posts_router.prefix}/new?owner_id={owner_name}&caption={caption}&tags={tags}"
        f"&published={test_post_published}",
        files=files
    )

    assert response.status_code == POST_ENTITY_BAD_TYPING_ERROR_STATUS_CODE, response.text


def test_get_post_should_succeed():
    response = posts_client.get(f"{posts_router.prefix}/{test_post_id}")
    assert response.status_code == REQUEST_IS_OK_STATUS_CODE, response.text
    data = response.json()
    assert data["caption"] == test_post_caption, f"Should be '{test_post_caption}'!"
    assert data["owner_id"] == test_post_owner_id, f"Should be '{test_post_owner_id}'!"
    assert data["id"] == test_post_id, f"Should be '{test_post_id}'!"


def test_get_post_should_fail():
    # lolita4
    post_id = uuid.uuid4()
    assert post_id != test_post_id
    response = posts_client.get(f"{posts_router.prefix}/{post_id}")
    assert response.status_code == 404, response.text
    assert response.json() == {"detail": f"The post with id: {post_id} cannot be found!"}


def test_get_post_image_should_succeed():
    response = posts_client.post(f"{posts_router.prefix}/{test_post_id}/get-image")
    assert response.status_code == REQUEST_IS_OK_STATUS_CODE, response.text


def test_get_post_image_should_fail():
    post_id = "445-ea"
    response = posts_client.post(f"{posts_router.prefix}/{test_post_id}/get-image")
    assert response.status_code == OBJECT_CANNOT_BE_FOUND_STATUS_CODE, response.text
    assert response.json() == {"detail": get_object_cannot_be_found_detail_message(post_id, ObjectType.POST)}


def test_add_comment_to_post_should_succeed():
    response = posts_client.post(f"{posts_router.prefix}/{test_post_id}/comments/add/{test_post_comment_id}")
    assert response.status_code == REQUEST_IS_OK_STATUS_CODE, response.text
    data = response.json()
    assert data["comments"] == [test_post_comment_id], f"Should be '[{test_post_comment_id}]'!"


def test_add_comment_to_post_should_fail():
    post_id = "445-ea"
    response = posts_client.post(f"{posts_router.prefix}/{post_id}/comments/add/{test_post_comment_id}")
    assert response.status_code == OBJECT_CANNOT_BE_FOUND_STATUS_CODE, response.text
    assert response.json() == {"detail": get_object_cannot_be_found_detail_message(post_id, ObjectType.POST)}

    comment_id = "445-ea"
    response = posts_client.post(f"{posts_router.prefix}/{test_post_id}/comments/add/{comment_id}")
    assert response.status_code == VALUE_LENGTH_ERROR_STATUS_CODE, response.text


def test_remove_comment_to_post_should_succeed():
    response = posts_client.post(f"{posts_router.prefix}/{test_post_id}/comments/remove/{test_post_comment_id}")
    assert response.status_code == REQUEST_IS_OK_STATUS_CODE, response.text
    data = response.json()
    assert data["comments"] == [], f"Should be '[]'!"


def test_remove_comment_to_post_should_fail():
    post_id = "445-ea"
    response = posts_client.post(f"{posts_router.prefix}/{post_id}/comments/remove/{test_post_comment_id}")
    assert response.status_code == OBJECT_CANNOT_BE_FOUND_STATUS_CODE, response.text
    assert response.json() == {"detail": get_object_cannot_be_found_detail_message(post_id, ObjectType.POST)}

    comment_id = "445-ea"
    response = posts_client.post(f"{posts_router.prefix}/{test_post_id}/comments/remove/{comment_id}")
    assert response.status_code == VALUE_LENGTH_ERROR_STATUS_CODE, response.text


def test_remove_all_comments_to_post_should_succeed():
    response = posts_client.post(f"{posts_router.prefix}/{test_post_id}/comments/remove-all")
    assert response.status_code == REQUEST_IS_OK_STATUS_CODE, response.text
    data = response.json()
    assert data["comments"] == [test_post_comment_id], f"Should be '[{test_post_comment_id}]'!"

    # Remove all comments
    response = posts_client.post(f"{posts_router.prefix}/{test_post_id}/comments/remove-all")
    assert response.status_code == REQUEST_IS_OK_STATUS_CODE, response.text
    data = response.json()
    assert data["comments"] == [], f"Should be '[]'!"


def test_remove_all_comments_to_post_should_fail():
    post_id = "445-ea"
    response = posts_client.post(f"{posts_router.prefix}/{test_post_id}/comments/remove-all")
    assert response.status_code == OBJECT_CANNOT_BE_FOUND_STATUS_CODE, response.text
    assert response.json() == {"detail": get_object_cannot_be_found_detail_message(post_id, ObjectType.POST)}


def test_delete_post_should_fail():
    user_id = 52
    # Delete the post
    response = posts_client.delete(f"{posts_router.prefix}/delete/{test_post_id}?user_id={user_id}")
    assert response.status_code == FORBIDDEN_REQUEST_STATUS_CODE, response.text
    assert response.json() == {"detail": get_forbidden_request_detail_message()}


def test_delete_post_should_succeed():
    # Delete the post
    response = posts_client.delete(f"{posts_router.prefix}/delete/{test_post_id}?user_id={test_post_owner_id}")
    data = response.json()
    assert f"{SUCCESSFUL_DELETION_MESSAGE_KEY}" in data
    assert data[f"{SUCCESSFUL_DELETION_MESSAGE_KEY}"] == f"{SUCCESSFUL_DELETION_MESSAGE_VALUE_FOR_POST}", \
        f"Should be '{SUCCESSFUL_DELETION_MESSAGE_VALUE_FOR_POST}'"

    # Verify that getting the deleted post doesn't work
    response = posts_client.get(f"{posts_router.prefix}/{test_post_id}")
    assert response.status_code == 404, response.text
