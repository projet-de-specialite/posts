from fastapi import FastAPI

# from project.src.app.routes.posts import posts_router
# from project.src.app.routes.tags import tags_router

app = FastAPI(
    title="Posts management",
    description="The PicShare API managing the posts and the tags",
    version="1.0.0"
)


@app.get("/ping")
async def pong():
    return {
        "ping": "pong!"
    }
