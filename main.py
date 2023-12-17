from fastapi import FastAPI, Depends
import aiomysql
from contextlib import asynccontextmanager
import db_handling
import os
from typing import Generator
from models import UserInput
import gpt_executor
import oauth


# 依存性注入用の関数
async def get_db() -> Generator:
    async with db_handling.db_pool.acquire() as conn:
        yield conn


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_handling.db_pool = await aiomysql.create_pool(
        host=os.getenv("MYSQL_HOSTNAME", 'dockerDB'),
        port=3306,
        user=os.getenv("MYSQL_USER", "hackathon_23_winter_12"),
        password=os.getenv("MYSQL_PASSWORD", 'password'),
        db=os.getenv("MYSQL_DATABASE", "hackathon_23_winter_12")
    )

    async with db_handling.db_pool.acquire() as conn:
        await db_handling.initialize_db(conn)

    yield

    db_handling.db_pool.close()
    await db_handling.db_pool.wait_closed()


app = FastAPI()
app.router.lifespan_context = lifespan


@app.get("/")
def read_root():
    return {"Hello": "world"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


@app.get("/recipe/{recipe_id}")
async def read_recipe(recipe_id: int, conn=Depends(get_db)):
    return await db_handling.get_recipe(conn, recipe_id)


@app.post("/add_recipe")
async def create_recipe(recipe_info: dict, conn=Depends(get_db)):
    result = await db_handling.add_recipe(conn, recipe_info)
    return result


@app.get("/recipes")
async def read_all_recipes(conn=Depends(get_db)):
    return await db_handling.get_all_recipes(conn)


@app.post("/process-text")
async def process_text(input_data: UserInput, conn=Depends(get_db)):
    recipe_info = await gpt_executor.executor(input_data.text)

    result = await db_handling.add_recipe(conn, recipe_info)
    return result


app.include_router(oauth.router, prefix="/oauth", tags=["oauth"])
