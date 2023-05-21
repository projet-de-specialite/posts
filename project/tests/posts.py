import os
import uuid

import sqlalchemy as _sql
import sqlalchemy.orm as _orm
from dotenv import load_dotenv
from fastapi.testclient import TestClient

import project.src.config.db.database as _database
from project.src.app.main import app
from project.src.app.routes.shared_constants_and_methods import (
    SUCCESSFUL_DELETION_MESSAGE_KEY, SUCCESSFUL_DELETION_MESSAGE_VALUE_FOR_POST)
from project.src.app.routes.posts import get_db, posts_router

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

test_post2_id = ""


def test_fetch_posts():
    response = posts_client.get(f"{posts_router.prefix}/")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == [], f"Should be [] because there is no posts yet!"


def test_fetch_latest_posts():
    response = posts_client.get(f"{posts_router.prefix}/latest/")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == [], f"Should be [] because there is no posts yet!"


def test_create_post_should_succeed():
    global test_post_id
    response = posts_client.post(
        f"{posts_router.prefix}/new",
        json={
            "image": test_post_image,
            "caption": test_post_caption,
            "tags": test_post_tags,
            "published": test_post_published,
            "owner_id": test_post_owner_id,
        },
    )

    assert response.status_code == 200, response.text
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


def test_get_post_should_succeed():
    response = posts_client.get(f"{posts_router.prefix}/{test_post_id}")
    assert response.status_code == 200, response.text
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


# I stopped on line 117 (routes/posts)
def test_delete_post_should_succeed():
    # Delete the post
    response = posts_client.delete(f"{posts_router.prefix}/delete/{test_post_id}")
    data = response.json()
    assert f"{ SUCCESSFUL_DELETION_MESSAGE_KEY }" in data
    assert data[f"{SUCCESSFUL_DELETION_MESSAGE_KEY}"] == f"{SUCCESSFUL_DELETION_MESSAGE_VALUE_FOR_POST}", \
        f"Should be '{SUCCESSFUL_DELETION_MESSAGE_VALUE_FOR_POST}'"

    # Verify that getting the deleted post doesn't work
    response = posts_client.get(f"{posts_router.prefix}/{test_post_id}")
    assert response.status_code == 404, response.text
