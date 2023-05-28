### Posts repository

## Running the app
- You must have **python 3.10+** <br>
  Check your python version with: `python3 --version` or `python --version`

- For the environment variables, you must have all the variables listed in the "**[.env.template](https://github.com/projet-de-specialite/posts/blob/main/.env.template)**" file. 
- The app is dockerized. Follow the following lines to try it!


  ```shell
    docker-compose config  # Will help you check if the configuration is fine.
    docker-compose up -d --build  # To build and start the databases & run the app.
  ```
  
# **Posts management**
#### The PicShare API managing the posts and the tags

---

<div>

> ### *The python classes*

<p>

```python
import uuid
import datetime
# Tag class
class Tag:
  id: uuid.UUID
  name: str
  slug: str
  posts: list[Post]
  created_on: datetime

# Post class
class Post:
  id: uuid
  image: str
  caption: str
  tags: list[Tag]
  published: bool
  owner_id: int
  likes: int
  published_on: datetime
  created_on: datetime
  updated_on: datetime
  
```

</p>

There are 2 principal path prefixes : 

- ### **/api/v1/posts**
- ### **/api/v1/tags**

</div>
<div>

> ### *Down are listed all the API's routes.*

<p>

- "**/api/v1/posts/**" (`GET`)

  Fetches the posts

  Required parameters: `none`

  Optional parameters:
  - **owners**: a list of integer (the owners id) <br>
  Gets all the posts made by the users with the specified ids. 
  It's a *union* of all their posts.
  - **tags**: a list of string (the tags slug) <br>
  Gets all the posts with the specified tags (**The post must have ALL of them**). 
  It's an *intersect* of all the fetched posts.
  - **skip**: an integer - `default = 0` <br>
  Excludes the first N posts from the fetched list and returns it.
  - **limit**: an integer - `default = 100` <br>
  Specifies the maximum number of posts in the list to return.

  <br>

  ```
  # example 1
  http://localhost:8000/api/v1/posts/

  # example 2 - returns the posts with owners 1 & 3 starting from the 3rd post
  http://localhost:8000/api/v1/posts/?owners=1&owners=3&skip=2

  # example 3
  http://localhost:8000/api/v1/posts/?owners=1&owners=3&tags=lolita&limit=50
  ```

</p>
<p>

- "**/api/v1/posts/latest/**" (`GET`)

  Same as "***/api/v1/posts/***" but fetches the **LATEST** posts

  ```
  # example 
  http://localhost:8000/api/v1/posts/latest/?owners=1&limit=50
  ```

</p>
<p>

- "**/api/v1/posts/{post_id}**" (`GET`)

  Fetches a post by its ID

  Required parameters: 
  - **post_id**: an uuid (the post id) <br>
  Gets the post with the specified id or return an error (`404`) when not found.

  Optional parameters: `none`

  ```
  # example
  http://localhost:8000/api/v1/posts/3fa99f64-5717-4562-b3fc-2c963f66afe4
  ```

</p>
<p>

- "**/api/v1/posts/{post_id}/get-image/**" (`GET`)

  Fetches a post's image by the ID of the post

  Required parameters: 
  - **post_id**: an uuid (the post id) <br>
  Gets the post's image or return an error (`404`) when not found.

  Optional parameters: `none`

  ```
  # example
  http://localhost:8000/api/v1/posts/3fa99f64-5717-4562-b3fc-2c963f66afe4/get-image
  ```

</p>
<p>

- "**/api/v1/posts/{post_id}**" (`PUT`)

  Likes or dislikes a post

  <p>

  Required parameters: 
  - **post_id**: an uuid (the post id) <br>
  Gets the post with the specified id or return an error (`404`) when not found.
  - **"like_action"**: an ***enum***. <br>
  Likes or dislikes a post.
  You have to choose between : **Like** and **Unlike** 
  
  </p>
  <p>

  ```python
  from enum import Enum
  class LikePostActionEnum(str, Enum):
    LIKE = "Like",
    UNLIKE = "Unlike"
  ```

  Optional parameters: `none`

  ```
  # example
  http://localhost:8000/api/v1/posts/3fa99f64-5717-4562-b3fc-2c963f66afe4?like_action=Like
  ```

  </p>
<p>

- "**/api/v1/posts/new**" (`POST`)

  Creates a post

  Required parameters: 
  - **file**: a file to upload
  - **caption**: a string (default = (`""`))
  - **tags**: a list of string (default = (`[]`))
  - **published**: a boolean (default = (`False`))
  - **owner_id**: the owner id (default = (`1`))

  Optional parameters: `none`

</p>
<p>

- "**/api/v1/posts/update/{post_id}**" (`PUT`)

  Updates an exiting post - Only the post's caption, tags and publication state can be updated.

  Required parameters: 
  - **post_id**: an uuid (the post id) <br>
  Gets the post with the specified id or return an error (`404`) when not found.
  
  - **user_id**: an integer (the user - performing the update - id) <br> 
  Will return an (`403`) error when the user performing the update is not the post's owner.

  Optional parameters: `none`

  ***Request body***

  ```json
  {
    "caption": "string",
    "tags": [
      {
        "name": "string"
      }
    ],
    "published": false
  }
  ```

</p>
<p>

- "**/api/v1/posts/delete/{post_id}**" (`DELETE`)

  Deletes an existing post

  Required parameters: 
  - **post_id**: an uuid (the post id) <br> 
  Gets the post with the specified id or return an error (`404`) when not found.
  
  - **user_id**: an integer (the user - performing the deletion - id) <br>
  Will return an (`403`) error when the user performing the deletion is not the post's owner.

  Optional parameters: `none`

</p>
<p>

- "**/api/v1/tags/**" (`GET`)

  Fetches the tags

  Required parameters: `none`

  Optional parameters:
  - **skip**: an integer - `default = 0` <br>
  Excludes the first N tags from the fetched list and returns it.
  - **limit**: an integer - `default = 100` <br>
  Specifies the maximum number of tags in the list to return.

  <br>

  ```
  # example 1
  http://localhost:8000/api/v1/tags/

  # example 2
  http://localhost:8000/api/v1/tags/?skip=2&limit=50
  ```

</p>
<p>

- "**/api/v1/tags/search/{characters}**" (`GET`)

  Fetches the tags with names containing the given characters

  Required parameters: 
  - **characters**: the characters to search (must be ***at least 3 characters***)

  Optional parameters:
  - **skip**: an integer - `default = 0` <br>
  Excludes the first N tags from the fetched list and returns it.
  - **limit**: an integer - `default = 100` <br>
  Specifies the maximum number of tags in the list to return.

  <br>

  ```
  # example 1
  http://localhost:8000/api/v1/tags/search/moon

  # example 2
  http://localhost:8000/api/v1/tags/search/moon?skip=2&limit=50
  ```

</p>
<p>

- "**/api/v1/tags/new**" (`POST`)

  Creates a tag
  
  The tag's ***name*** must be ***at least 3 characters*** long! The tag's name is ***unique*** so is the slug.

  Required parameters: 
  - **tag**: a tag object (See down)

  Optional parameters: `none`

  ***Request body***

  ```json
  {
    "name": "string"
  }
  ```

</p>
<p>

- "**/api/v1/tags/{tag_slug}**" (`POST`)

  Fetches a tag by its slug - the exact slug (NOT A PARTIAL SEARCH)

  Required parameters: 
  - **tag_slug**: a string 

  Optional parameters: `none`

  ```
  # example
  http://localhost:8000/api/v1/tags/lolita
  ```

</p>
</div>
<div>

> ### *The models schemas*

<p>

- ***post schema***

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "image": "string",
  "caption": "string",
  "tags": [],
  "published": false,
  "owner_id": 0,
  "likes": 0,
  "published_on": "2023-04-19T19:10:03.100Z",
  "created_on": "2023-04-19T19:10:03.100Z",
  "updated_on": "2023-04-19T19:10:03.100Z"
}
```

- ***tag schema***

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
  "name": "string",
  "slug": "string",
  "posts": [
    {
      "image": "string",
      "caption": "string",
      "tags": [],
      "published": false,
      "owner_id": 0
    }
  ],
  "created_on": "2023-04-19T19:18:14.141Z"
}
```

</p>
</div>