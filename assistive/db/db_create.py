from assistive.config_read import config

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
        CREATE TABLE plants (
        id                INTEGER PRIMARY KEY AUTOINCREMENT
                                NOT NULL,
        name              TEXT    NOT NULL,
        birthdate         TEXT    NOT NULL,
        user_id           INTEGER NOT NULL
                                REFERENCES users (id) ON DELETE CASCADE
                                                        ON UPDATE CASCADE,
        basic_description TEXT,
        individual_id     INTEGER NOT NULL
    );""")
    conn.cursor.execute("""
        CREATE TABLE plants_history (
        id          INTEGER PRIMARY KEY AUTOINCREMENT
                            NOT NULL,
        plant_id    INTEGER REFERENCES plants (id) ON DELETE CASCADE
                                                ON UPDATE CASCADE
                            NOT NULL,
        date        TEXT    DEFAULT (datetime('now', 'localtime') ),
        description TEXT,
        image_id    TEXT
    );""")
    conn.cursor.execute("""
        CREATE TABLE users (
        id             INTEGER PRIMARY KEY AUTOINCREMENT
                            UNIQUE
                            NOT NULL,
        name           TEXT    NOT NULL,
        id_in_telegram INTEGER UNIQUE
                            NOT NULL,
        id_group       INTEGER REFERENCES [group] (id) ON DELETE CASCADE
                                                    ON UPDATE CASCADE
    );""")
    admins = config["ADMIN"].split(",")
    for c in admins:
        conn.cursor.execute("INSERT INTO 'users' ('id_in_telegram','name') VALUES (?, ?)",(c,"Admin"))
    conn.conn.commit()