import datetime
import sqlite3

import pytz

from BACKEND.Models.FDataBase import FDataBase


class SQL(FDataBase):
    def __init__(self, db):
        super(SQL, self).__init__(db)
        self.__db = db
        self.__cur = self.__db.cursor()

    def get_user_id(self, auth):
        try:
            ans = self.__cur.execute("SELECT ID FROM lk WHERE user_login = ? or "
                                     "user_email = ? or user_num = ?",
                               (auth, auth, auth)).fetchone()
            return ans
        except sqlite3.Error as e:
            print("(Ошибка API) Ошибка метода get_user_id: " + str(e))

    def get_user_info(self, id_):
        try:
            ans = self.__cur.execute("SELECT * FROM lk WHERE ID = ?",
                               (id_,)).fetchone()
            return ans
        except sqlite3.Error as e:
            print("(Ошибка API) Ошибка метода get_user_info: " + str(e))

    def check_secret_key(self, secret_key):
        try:
            ans = self.__cur.execute("SELECT token_info FROM api WHERE token = ?",
                               (secret_key,)).fetchone()
            if ans:
                return True
            else:
                return False
        except sqlite3.Error as e:
            print("(Ошибка API) Ошибка метода check_secret_key: " + str(e))

    def add_token(self, token):
        try:
            self.__cur.execute("INSERT INTO revoked_token VALUES (NULL, ?)", (token, ))
            self.__db.commit()
        except sqlite3.Error as e:
            print("(Ошибка API) Ошибка метода add_token: " + str(e))

    def check_if_token_in_blacklist(self, jti):
        try:
            ans = self.__cur.execute("SELECT ID FROM revoked_tokens WHERE jwt = ?", (jti, )).fetchone()
            if ans:
                return True
            else:
                return False
        except sqlite3.Error as e:
            print("(Ошибка API) Ошибка метода check_if_token_in_blacklist: " + str(e))

    def addUser_api(self, login, telephone, email, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM lk WHERE user_email LIKE '{email}'")
            if self.__cur.fetchone()['count'] > 0:
                # print('Пользователь с таким email уже существует. . .')
                return {"error": "email"}
            self.__cur.execute(f"SELECT COUNT() as `count` FROM lk WHERE user_login LIKE '{login}'")
            if self.__cur.fetchone()['count'] > 0:
                # print('Пользователь с таким login уже существует. . .')
                return {"error": "login"}
            self.__cur.execute(f"SELECT COUNT() as `count` FROM lk WHERE user_num LIKE '{telephone}'")
            if self.__cur.fetchone()['count'] > 0:
                # print('Пользователь с таким email уже существует. . .')
                return {"error": "telephone"}
            tm = datetime.datetime.now(pytz.timezone('Europe/Moscow'))
            self.__cur.execute("INSERT INTO lk VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)",
                               (None, None, email, login, telephone, hpsw, tm.strftime("%Y-%m-%d %H.%M.%S"), 'Участник', 0, 0,
                                False))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД:\n" + str(e))
            return False
        return {"error": "ok"}


