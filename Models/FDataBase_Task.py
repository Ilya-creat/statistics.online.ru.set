import datetime
import sqlite3


class Contest_SQL:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()  # работа с БД

    def user_login_contest(self, user, contest_name):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM {contest_name} WHERE USER_ID LIKE '{user}'")
            if self.__cur.fetchone()['count'] > 0:
                # Пользователь зарегистрирован
                return True
            return False
        except sqlite3.Error as e:
            print('Ошибка в user_login_contest:', e)
            return False

    def reg_user_in_dbase(self, database, user):
        try:
            self.__cur.execute(f"INSERT INTO {database} VALUES (NULL, ?, ?, ?, ? )",
                               (user, 0, 1, datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")))
            self.__cur.execute(f"SELECT COUNT() as `count` FROM {database} WHERE user_id LIKE '{user}'")
            if self.__cur.fetchone()['count'] > 0:
                # Пользователь зарегистрирован
                self.__db.commit()
                return True
            return False
        except sqlite3.Error as e:
            print('Ошибка в reg_user_in_dbase:', e)
            return False

    def getContestInfo_all_count(self, _list_, begin, interval):
        try:
            _list_return_ = []
            for i in range(begin, len(_list_), interval):
                db_list = 0
                self.__cur.execute(f"SELECT COUNT(*) as `count` FROM {_list_[i]}")
                db_list = self.__cur.fetchone()['count']
                _list_return_.append(db_list)
            return _list_return_
        except sqlite3.Error as e:
            print("Ошибка в БД getContestInfo_all_count: " + str(e))
            return False

    def checkRegister(self, base, name, forms):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM {base} WHERE {name} LIKE '{forms}'")
            if self.__cur.fetchone()['count'] > 0:
                print(f'Пользователь с таким {forms} уже существует. . .')
                return False
            else:
                return True
        except sqlite3.Error as e:
            print("Ошибка получения запроса в checkRegister:\n" + str(e))
            return False

    def get_status_active(self, contest_base, user):
        try:
            self.__cur.execute(f"SELECT status_active FROM {contest_base} WHERE user_id = '{user}'")
            active = self.__cur.fetchone()[0]
            if active == 2:
                return True
            return False
        except sqlite3.Error as e:
            print("Ошибка получения запроса в get_status_active:\n" + str(e))
            return False
