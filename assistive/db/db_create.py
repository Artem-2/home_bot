#Создание базы данных в случае если ее нет

def db_create(conn):
    conn.cursor.execute("""
        CREATE TABLE basket (
            id       INTEGER PRIMARY KEY AUTOINCREMENT
                            UNIQUE
                            NOT NULL,
            id_group INTEGER NOT NULL
                            REFERENCES [group] (id) ON DELETE CASCADE
                                                    ON UPDATE CASCADE,
            product  TEXT
        );""")
    conn.cursor.execute("""
        CREATE TABLE [group] (
            id         INTEGER PRIMARY KEY AUTOINCREMENT
                            NOT NULL
                            UNIQUE,
            group_name TEXT    NOT NULL
        );""")
    conn.cursor.execute("""
        CREATE TABLE users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT
                            UNIQUE
                            NOT NULL,
            name     TEXT    NOT NULL,
            id_in_tg INTEGER UNIQUE
                            NOT NULL,
            id_group INTEGER NOT NULL
                            REFERENCES [group] (id) ON DELETE CASCADE
                                                    ON UPDATE CASCADE
        );""")
    conn.cursor.execute("""
        CREATE TABLE plants (
            id        INTEGER PRIMARY KEY AUTOINCREMENT
                            NOT NULL,
            name              NOT NULL,
            birthdate TEXT    NOT NULL,
            user_id   INTEGER NOT NULL
                            REFERENCES users (id) ON DELETE CASCADE
                                                    ON UPDATE CASCADE
        );""")
    conn.conn.commit()