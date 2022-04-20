from datetime import datetime
from os import environ

from fastapi import FastAPI
import databases
from sqlalchemy import select
from schema import PostCreate, PostUpdate
from models import posts_table

app = FastAPI()

DB_USER = environ.get("DB_USER", "fast_teach")
DB_PASSWORD = environ.get("DB_PASSWORD", "fast_teach")
DB_HOST = environ.get("DB_HOST", "localhost")
DB_NAME = "fast_teach"
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
)
database = databases.Database(SQLALCHEMY_DATABASE_URL)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def root():
    query = (
        select(
            [
                posts_table.c.id,
                posts_table.c.created_at,
                posts_table.c.title,
                posts_table.c.content,
            ]
        )
            .select_from(posts_table)
    )
    return await database.fetch_all(query)


@app.post("/create-post")
async def create_post(request: PostCreate):
    query = posts_table.insert().values(
        created_at=datetime.now(), title=request.title, content=request.content
    )
    post_id = await database.execute(query)
    return {"some_key": post_id}


@app.post("/update-post")
async def update_post(request: PostUpdate):
    request = dict(request)
    post_id = request["id"]
    del request["id"]
    request = {key: value for key, value in request.items() if value is not None}
    query = posts_table.update().where(posts_table.c.id == post_id).values(**request).returning(
        posts_table.c.id,
        posts_table.c.created_at,
        posts_table.c.title,
        posts_table.c.content, )
    await database.execute(query=query)
    return await database.fetch_one(query)
