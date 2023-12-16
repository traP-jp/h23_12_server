from typing import Generator
import aiomysql
from fastapi import HTTPException

dp_pool = None


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
                image BLOB
            )
        """)

        # デフォルトレシピの挿入 (例)
        default_recipes = [
            ("Recipe 1", "Comment 1", "Ingredients 1", "Seasoning 1", "Instruction 1", None),
            ("Recipe 2", "Comment 2", "Ingredients 2", "Seasoning 2", "Instruction 2", None),
            # 他のレシピを追加
        ]

        for recipe in default_recipes:
            await cursor.execute("""
                INSERT INTO recipes (name, comment, ingredient, seasoning, instruction, image)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, recipe)

        await conn.commit()


async def get_recipe(conn, recipe_id: int):
    """
    Returns recipe information for a given recipe_id
    """
    query = "SELECT * FROM recipes WHERE recipe_id = %s"

    async with conn.cursor() as cursor:
        await cursor.execute(query, (recipe_id,))
        recipe = await cursor.fetchone()

        if recipe:
            return recipe
        else:
            raise HTTPException(status_code=404, detail="No recipe found with the specified ID.")


async def add_recipe(conn, recipe_info: dict):
    """
    Add the given recipe_info to the DB table.
    """
    query = "INSERT INTO recipes (name, comment, ingredient, seasoning, instruction) VALUES (%s, %s, %s, %s, %s)"

    recipe_info['ingredient'] = ', '.join(recipe_info['ingredient'])
    recipe_info['seasoning'] = ', '.join(recipe_info['seasoning'])
    recipe_info['instruction'] = ', '.join(recipe_info['instruction'])

    # ToDo: You have to check what data is contained(is contained detailed_description?)
    recipe_info = [recipe_info[key] for key in recipe_info.keys()][:5]

    try:
        async with conn.cursor() as cursor:
            await cursor.execute(query, recipe_info)
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
            return all_recipes
    except aiomysql.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
