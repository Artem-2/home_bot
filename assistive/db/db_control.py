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
        table_array = ["users"]
        flag = 0
        for t in table_array:
            result = self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='" + t + "';")
            if result.fetchone()==None :
                flag = 1
        if flag == 1:
            db_create(self)
    #необходима для тестов потом удалить
    def get(self):
        print("работает")