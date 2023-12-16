from typing import Generator
import aiomysql
from fastapi import HTTPException

dp_pool = None


async def get_recipe(conn, recipe_id: int):
    """
    Returns recipe information for a given recipe_id
    """
    query = "SELECT * FROM recipes WHERE id = %s"

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
    query = "SELECT id, name, image FROM recipes"

    try:
        async with conn.cursor() as cursor:
            await cursor.execute(query)
            all_recipes = await cursor.fetchall()
            return all_recipes
    except aiomysql.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
