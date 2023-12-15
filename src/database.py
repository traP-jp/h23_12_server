# Module Imports
import mariadb
import sys
import os


def return_recipe(index):
    """
    Retrieves a recipe with a given index from the database and returns the recipe information.

    Parameters
    ----------
    index: int
        id of the recipe you want to retrieve

    Returns
    -------
    recipe: json
        Recipe information for the given index
    """
    query = "SELECT * FROM recipes WHERE id = ?"

    try:
        cur = connection.cursor()
        cur.execute(query, (index,))

        recipe = cur.fetchone()
        if recipe:
            return recipe
        else:
            return "No recipe found with the specified ID."
    except mariadb.Error as e:
        print(f"Error: {e}")
        return None

    finally:
        cur.close()


def generate_recipe():
    pass


def add_recipe(recipe_info):
    """
    Add the given recipe_info to the DB table.

    Parameters
    ----------
    recipe_info: dict
        Stores data including name, comment, ingredient, seasoning, and instruction

    Returns
    -------

    """
    query = "INSERT INTO recipes (name, comment, ingredient, seasoning, instruction) VALUES (?, ?, ?, ?, ?)"

    recipe_info['comment'] = ''.join(recipe_info['comment'])
    recipe_info['ingredient'] = ', '.join(recipe_info['ingredient'])
    recipe_info['seasoning'] = ', '.join(recipe_info['seasoning'])
    recipe_info['instruction'] = ', '.join(recipe_info['instruction'])

    recipe_info = [recipe_info[key] for key in recipe_info.keys()][:5]

    print(recipe_info)
    try:
        cur = connection.cursor()
        cur.execute(query, recipe_info)
        connection.commit()
        print(f"{recipe_info[0]}: Recipe added.")
    except mariadb.Error as e:
        print(f"Error: {e}")

    finally:
        cur.close()


def create_table(table_name):
    """
    Create a table in DB according to the given table_name.

    Parameters
    ----------
    table_name: str

    Returns
    -------

    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS recipes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        name VARCHAR(255),
        comment TEXT,
        ingredient TEXT,
        seasoning TEXT,
        instruction TEXT,
        picture BLOB
    );
    """

    # Execute the query
    try:
        cur = connection.cursor()
        cur.execute(create_table_query)
        connection.commit()
        print("Table 'recipes' created successfully.")
    except mariadb.Error as e:
        print(f"Error creating table: {e}")

    finally:
        cur.close()


# Connect to MariaDB Platform
try:
    user = os.getenv("MARIADB_USER", "root")
    password = os.getenv("MARIADB_PASSWORD", "password")
    host = os.getenv("MARIADB_HOSTNAME", "dockerDB")
    dbname = os.getenv("MARIADB_DATABASE", "hackathon_23winter_12")
    connection = mariadb.connect(
        user=user,
        password=password,
        host=host,
        port=3306,
        database=dbname
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)


# Close cursor and connection
connection.close()
