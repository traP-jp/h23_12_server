# Module Imports
import mariadb
import sys
import os

# Connect to MariaDB Platform
try:
    user = os.getenv("NS_MARIADB_USER", "root")
    password = os.getenv("NS_MARIADB_PASSWORD", "password")
    host = os.getenv("NS_MARIADB_HOSTNAME", "dockerDB")
    dbname = os.getenv("NS_MARIADB_DATABASE", "hackathon_23winter_12")
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
