from fastapi import FastAPI, Depends
import aiomysql
import db_handling
import os
from typing import Generator

app = FastAPI()


# 依存性注入用の関数
async def get_db() -> Generator:
    async with db_handling.db_pool.acquire() as conn:
        yield conn


# アプリケーションの起動時にデータベース接続プールを初期化
@app.on_event("startup")
async def startup():
    db_handling.db_pool = await aiomysql.create_pool(
        host=os.getenv("MARIADB_HOSTNAME"),
        port=3306,
        user=os.getenv("MARIADB_USER"),
        password=os.getenv("MARIADB_PASSWORD"),
        db=os.getenv("MARIADB_DATABASE")
    )


# アプリケーションのシャットダウン時にデータベース接続プールを閉じる
@app.on_event("shutdown")
async def shutdown():
    db_handling.db_pool.close()
    await db_handling.db_pool.wait_closed()


@app.get("/")
def read_root():
    return {"Hello": "world"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


@app.get("/recipe/{recipe_id}")
async def read_recipe(recipe_id: int, conn=Depends(get_db)):
    return await db_handling.get_recipe(conn, recipe_id)


@app.post("/recipes")
async def create_recipe(recipe_info: dict, conn=Depends(get_db)):
    result = await db_handling.add_recipe(conn, recipe_info)
    return result


@app.get("/recipes")
async def read_all_recipes(conn=Depends(get_db)):
    return await db_handling.get_all_recipes(conn)


app.include_router(oauth.router, prefix="/oauth", tags=["oauth"])
