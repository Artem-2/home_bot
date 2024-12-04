from assistive.db.db_control import BotDB
import os.path

try:
    p = os.path.join(".","assistive","db","DB.db")
    BotDB = BotDB(p)
except:
    print("Не удается подключиться к базе данных")
