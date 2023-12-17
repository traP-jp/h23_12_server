import apis.oauth as oauth
import apis.dish as dish
from pydantic import BaseModel, Base64Bytes
from logging import getLogger
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
import aiomysql
from contextlib import asynccontextmanager
import db_handling
import os
from typing import Generator, List, Optional
from models import UserInput
import gpt_executor
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

logger = getLogger("uvicorn.app")


# 依存性注入用の関数
async def get_db() -> Generator:
    async with db_handling.db_pool.acquire() as conn:
        yield conn


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_handling.db_pool = await aiomysql.create_pool(
        user = os.getenv("NS_MARIADB_USER"),
        password = os.getenv("NS_MARIADB_PASSWORD"),
        host = os.getenv("NS_MARIADB_HOSTNAME"),
        db = os.getenv("NS_MARIADB_DATABASE"),
        port=3306
    )

    async with db_handling.db_pool.acquire() as conn:
        await db_handling.initialize_db(conn)

    yield

    db_handling.db_pool.close()
    await db_handling.db_pool.wait_closed()


app = FastAPI()
app.router.lifespan_context = lifespan

origins = [
    "http://localhost:4321",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GetPingResponce(BaseModel):
    ping: str

@app.get("/ping", response_model=GetPingResponce, operation_id="get_ping")
def get_ping():
    return GetPingResponce(ping="pong")

class GetRecipeResponce(BaseModel):
    recipe_id: int
    created_at: datetime
    updated_at: datetime
    name: str
    comment: str
    ingredient: List[str] | str
    seasoning: List[str] | str
    instruction: List[str] | str
    image: Base64Bytes | None

@app.get("/recipe/{recipe_id}", response_model=GetRecipeResponce, operation_id="get_recipe", tags=["recipe"])
async def read_recipe(recipe_id: int, conn=Depends(get_db)):
    res = await db_handling.get_recipe(conn, recipe_id)
    imgBytes = None
    if res["image"] != None:
        imgBytes = Base64Bytes(imgBytes)
    return GetRecipeResponce(
        recipe_id=res["recipe_id"],
        created_at=res["created_at"],
        updated_at=res["updated_at"],
        name=res["name"],
        comment=res["comment"],
        ingredient=res["ingredient"],
        seasoning=res["seasoning"],
        instruction=res["instruction"],
        image=imgBytes
    )

class AddRecipeResponse(BaseModel):
    message: str

@app.post("/add_recipe", operation_id="post_recipe", tags=["recipe"])
async def create_recipe(recipe_info: dict, conn=Depends(get_db)):
    result = await db_handling.add_recipe(conn, recipe_info)
    return AddRecipeResponse(message=result["message"])

class InnerGetRecipesResponce(BaseModel):
        recipe_id: int
        name: str
        image: Base64Bytes | None

@app.get("/recipes", operation_id="get_recipes", tags=["recipe"], response_model=InnerGetRecipesResponce)
async def read_all_recipes(conn=Depends(get_db)):
    result = await db_handling.get_all_recipes(conn)
    resp: List[InnerGetRecipesResponce] = []
    for _i, res in enumerate(result):
        imgBytes = None
        print(res)
        if res["image"] != None:
            imgBytes = Base64Bytes(res["image"])
        resp.append(InnerGetRecipesResponce(
            recipe_id=res["recipe_id"],
            name=res["name"],
            image=imgBytes))
    return resp

@app.post("/process-text", operation_id="post_recipe_gen_text", tags=["recipe"])
async def process_text(input_data: UserInput, conn=Depends(get_db)):
    recipe_info = await gpt_executor.executor(input_data.text)

    result = await db_handling.add_recipe(conn, recipe_info)
    return AddRecipeResponse(message=result["message"])


app.include_router(oauth.router, prefix="/oauth", tags=["oauth"])
app.include_router(dish.router, prefix="/dish", tags=["dish"])