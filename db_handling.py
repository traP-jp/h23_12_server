import aiomysql
import json
import os
import asyncio
from fastapi import HTTPException
import base64
import aiofiles
import aiofiles.os as aio_os
from pprint import pprint

dp_pool = None


async def load_json_async(file_path):
    async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
        data = json.loads(await file.read())
        recipe_info = {
            "name": data["name"],
            "comment": data["comment"],
            "ingredient": data["ingredient"],
            "seasoning": data["seasoning"],
            "instruction": data["instruction"],
            "image": data.get("image")  # "image" キーがあれば追加
        }
        return recipe_info


async def load_recipes_from_directory(directory):
    recipes = []
    # ディレクトリ内のファイルを非同期的にリストアップ
    filenames = await aio_os.listdir(directory)
    for filename in filenames:
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            recipe = await load_json_async(file_path)
            recipes.append(recipe)
    return recipes


async def initialize_db(conn):
    async with conn.cursor() as cursor:
        # テーブルの作成
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                recipe_id INT AUTO_INCREMENT PRIMARY KEY,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                name VARCHAR(255),
                comment TEXT,
                ingredient TEXT,
                seasoning TEXT,
                instruction TEXT,
                image MEDIUMBLOB
            )
        """)

        # default_recipes ディレクトリからレシピを読み込む
        default_recipes = await load_recipes_from_directory('./default_recipes')

        # 各レシピをデータベースに追加
        for recipe_info in default_recipes:
            await add_recipe(conn, recipe_info)

        await conn.commit()


     

# async def get_recipe(conn, recipe_id: int):
#     """
#     Returns recipe information for a given recipe_id
#     """
#     query = "SELECT * FROM recipes WHERE recipe_id = %s"
#
#     async with conn.cursor() as cursor:
#         await cursor.execute(query, (recipe_id,))
#         recipe_row = await cursor.fetchone()
#
#         if recipe_row:
#             recipe = {
#                 'recipe_id': recipe_row[0],
#                 'created_at': recipe_row[1],
#                 'updated_at': recipe_row[2],
#                 'name': recipe_row[3],
#                 'comment': recipe_row[4],
#                 'ingredient': recipe_row[5].split(', ') if recipe_row[5] else [],
#                 'seasoning': recipe_row[6].split(', ') if recipe_row[6] else [],
#                 'instruction': recipe_row[7].split(', ') if recipe_row[7] else [],
#                 'image': recipe_row[8]
#             }
#             return recipe
#         else:
#             raise HTTPException(status_code=404, detail="No recipe found with the specified ID.")

async def get_recipe(conn, recipe_id: int):
    """
    Returns recipe information for a given recipe_id
    """
    query = "SELECT * FROM recipes WHERE recipe_id = %s"

    async with conn.cursor() as cursor:
        await cursor.execute(query, (recipe_id,))
        recipe_row = await cursor.fetchone()

        if recipe_row:
            print(recipe_row[5])
            recipe = {
                'recipe_id': recipe_row[0],
                'created_at': recipe_row[1],
                'updated_at': recipe_row[2],
                'name': recipe_row[3],
                'comment': recipe_row[4],
                'ingredient': recipe_row[5].split(", "),
                'seasoning': recipe_row[6].split(", "),
                'instruction': recipe_row[7].split(", "),
                'image': recipe_row[8]
            }
            return recipe
        else:
            raise HTTPException(status_code=404, detail="No recipe found with the specified ID.")


async def add_recipe(conn, recipe_info: dict):
    """
    Add the given recipe_info to the DB table.
    """
    query = "INSERT INTO recipes (name, comment, ingredient, seasoning, instruction, image) VALUES (%s, %s, %s, %s, %s, %s)"

    recipe_info['ingredient'] = ', '.join(recipe_info['ingredient'])
    recipe_info['seasoning'] = ', '.join(recipe_info['seasoning'])
    recipe_info['instruction'] = ', '.join(recipe_info['instruction'])

    # 画像データがある場合は、そのまま使用する
    image_data = recipe_info.get('image')

    recipe_data = [recipe_info[key] for key in ['name', 'comment', 'ingredient', 'seasoning', 'instruction']] + [
        image_data]

    try:
        async with conn.cursor() as cursor:
            await cursor.execute(query, recipe_data)
            await conn.commit()
            return {"message": "Recipe added successfully"}
    except aiomysql.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


async def get_all_recipes(conn):
    query = "SELECT recipe_id, name, image FROM recipes"

    try:
        async with conn.cursor() as cursor:
            await cursor.execute(query)
            all_recipes = await cursor.fetchall()
            all_recipes = [{'recipe_id': recipe_id, 'name': name, 'image': image} for recipe_id, name, image in
                           all_recipes]
            return all_recipes
    except aiomysql.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
