import os
from dotenv import load_dotenv, find_dotenv

def read_env(env_file_path="config.env"):
    try:
        load_dotenv(dotenv_path=env_file_path, verbose=True)  # verbose выводит сообщение об успешном чтении
        return dict(os.environ)
    except FileNotFoundError:
        print("Файл .env не найден.")
        return None


config = read_env()