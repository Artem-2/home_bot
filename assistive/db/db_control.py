import sqlite3 
from assistive.db.db_create import db_create
#доделать создание преподавателя admina

semaphore = 0
#Семафор для защиты базы при большом количестве запросов
def semaphore_begin():
    global semaphore
    if semaphore == 0:
        semaphore = semaphore + 1
    else:
        s = semaphore
        min = 0
        while s != min:
            if semaphore - s < 0:
                min = min + ((-1)*(semaphore - s))

def semaphore_end():
    global semaphore
    semaphore = semaphore - 1

class BotDB:
    def __init__(self, db_file):
        #подключение к базе данных
        self.conn = sqlite3.connect(db_file)
        self.conn.execute("PRAGMA foreign_keys = 1")
        self.cursor = self.conn.cursor()
        table_array = ["users","plants","plants_history","group","basket"]
        flag = 0
        for t in table_array:
            result = self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='" + t + "';")
            if result.fetchone()==None :
                flag = 1
        if flag == 1:
            db_create(self)
    #######################################################################
    #добавление нового пользователя
    def user_add(self, id_in_telegram, name):
        semaphore_begin()
        self.cursor.execute("INSERT INTO 'users' ('id_in_telegram','name') VALUES (?, ?)",(id_in_telegram,name))
        self.conn.commit()
        r = self.cursor.lastrowid
        semaphore_end()
        return r
    #######################################################################
    #добавление нового растения вызывается в planats_control в process_plant_description
    def plant_add(self, name, birthdate, basic_description, id_in_telegram):
        semaphore_begin()
        result = self.cursor.execute("""SELECT individual_id FROM plants  WHERE user_id = (SELECT id FROM users WHERE id_in_telegram = ?);""", (id_in_telegram,))
        r = result.fetchall()
        i = 0
        flag = 0
        arr = []
        for a in r:
            arr.append(a[0])
        while flag == 0:
            i+=1
            if str(i) in arr:
                flag = 0
            else:
                print(str(i) + " = " + str(arr))
                flag = 1

        self.cursor.execute("""
        INSERT INTO plants (name, birthdate, basic_description, user_id, individual_id)
        VALUES (?, ?, ?, (
            SELECT id 
            FROM users 
            WHERE id_in_telegram = ?
        ),?)
        """, (name, birthdate, basic_description, id_in_telegram, str(i)))
        self.conn.commit()
        r = self.cursor.lastrowid
        semaphore_end()
        return str(i)
    #######################################################################
    #добавляет новую запись в историю расстений 
    def plant_history_add(self, plant_id, description, image_id):
        semaphore_begin()
        #добавление нового пользователя
        self.cursor.execute("INSERT INTO 'plants_history' ('plant_id', 'description', 'image_id') VALUES (?, ?, ?)",(plant_id, description, image_id))
        self.conn.commit()
        r = self.cursor.lastrowid
        semaphore_end()
        return r
    #######################################################################
    #получить список добавленыйх расстений
    def get_plants_list(self, user_id):
        semaphore_begin()
        #добавление нового пользователя
        result = self.cursor.execute("SELECT individual_id, name FROM plants WHERE user_id = (SELECT id FROM users WHERE id_in_telegram = ?) AND individual_id NOT LIKE '%-ARCHIVED'", (user_id,))
        r = result.fetchall()
        semaphore_end()
        return r
    #######################################################################
    #получить историю расстений
    def plant_history_get(self, user_id, plant_id):
        semaphore_begin()
        #добавление нового пользователя
        result = self.cursor.execute("SELECT date, description, image_id  FROM plants_history WHERE plant_id = (SELECT id  FROM plants WHERE user_id = (SELECT id FROM users WHERE id_in_telegram = ?) and individual_id = ?)",(user_id, plant_id))
        r = result.fetchall()
        semaphore_end()
        return r
    #######################################################################
    #перевод расстения в статус ARCHIVED
    def plant_ARCHIVED(self, user_id, plant_id):
        semaphore_begin()
        self.cursor.execute("""
        UPDATE plants
        SET individual_id = individual_id || '-ARCHIVED'
        WHERE user_id = (SELECT id FROM users WHERE id_in_telegram = ?) 
        AND individual_id = ?
        """, (user_id, plant_id))
        self.conn.commit()
        semaphore_end()