def db_create(conn):
    conn.cursor.execute("""
        CREATE TABLE users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT
                            UNIQUE
                            NOT NULL,
            name     TEXT,
            id_in_tg INTEGER UNIQUE,
            id_group INTEGER
        );
        """)
    conn.conn.commit()