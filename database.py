# Module Imports
import mariadb
import sys
import os

# Connect to MariaDB Platform
try:
    user = os.getenv("NS_MARIADB_USER")
    password = os.getenv("NS_MARIADB_PASSWORD")
    host = os.getenv("NS_MARIADB_HOSTNAME")
    dbname = os.getenv("NS_MARIADB_DATABASE")
    conn = mariadb.connect(
        user=user,
        password=password,
        host=host,
        port=3306,
        database=dbname
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()
