import mariadb
import sys


DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'tiriantrains_db'
}

def get_db_connection():
    try:
        conn = mariadb.connect(
            **DB_CONFIG
        )
        print(f'Connected to {DB_CONFIG["database"]} successfully!')
        return conn
    except mariadb.Error as e:
        print(f'Error connecting to {DB_CONFIG["database"]}: {e}')
        sys.exit(1)


# test database connection
if __name__ == '__main__':
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("show tables")
    tables = cursor.fetchall()
    print("Tables in the database: ", tables)

    cursor.close()
    conn.close()