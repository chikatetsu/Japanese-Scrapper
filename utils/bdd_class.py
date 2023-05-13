import colorama
import mysql.connector
from dotenv import load_dotenv
import os


class ConnectionDatabase:
    __instance = None
    cursor = None
    conn = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.conn = cls.__instance.__get_conn()
            cls.__instance.cursor = cls.__instance.conn.cursor()
        return cls.__instance


    @staticmethod
    def __get_conn():
        colorama.init()
        load_dotenv()

        try:
            conn = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME"),
            )
        except Exception as e:
            print(colorama.Fore.RED, "Impossible de se connecter à la base de données :", e, colorama.Style.RESET_ALL)
            exit()
        print("Connecté à la base de données")
        return conn


    def close(self):
        self.cursor.close()
        self.conn.close()
