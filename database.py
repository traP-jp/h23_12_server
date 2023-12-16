# Module Imports
import mariadb
import sys
import os

# Connect to MariaDB Platform
try:
    user = os.getenv("MARIADB_USER", "root")
    password = os.getenv("MARIADB_PASSWORD", "password")
    host = os.getenv("MARIADB_HOSTNAME", "dockerDB")
    dbname = os.getenv("MARIADB_DATABASE", "hackathon_23winter_12")
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