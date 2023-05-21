from dotenv import load_dotenv
from fastapi import FastAPI

from project.src.app.routes.posts import posts_router
from project.src.app.routes.tags import tags_router
from project.src.config.db.init_database import add_tables_to_picshare_database

load_dotenv()

app = FastAPI(
    title="Posts management",
    description="The PicShare API managing the posts and the tags",
    version="1.0.0"
)


@app.on_event("startup")
async def startup_event():
    add_tables_to_picshare_database()


app.include_router(posts_router)
app.include_router(tags_router)
