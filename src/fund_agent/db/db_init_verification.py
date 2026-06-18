from db_connection import get_db_connection

with get_db_connection() as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cursor.fetchall()
        for table in tables:
            print(table[0])
