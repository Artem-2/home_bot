from assistive.db.db_control import BotDB
import os.path

#Подключенение к базе данных, происходит при любом первом запросе в БД
try:
    p = os.path.join(".","assistive","db","DB.db")
    BotDB = BotDB(p)
except:
    print("Не удается подключиться к базе данных")
