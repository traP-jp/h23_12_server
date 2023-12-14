#!/bin/bash

# MySQLサーバーの詳細
SERVER="localhost"
USER="your_username"
PASSWORD="your_password"

# 作成するデータベースの名前
DATABASE="my_database"

# MySQLコマンドを使用してデータベースを作成
mysql -h $SERVER -u $USER -p$PASSWORD -e "CREATE DATABASE $DATABASE;"
