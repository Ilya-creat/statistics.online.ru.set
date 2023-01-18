import datetime
import sqlite3
import threading

import pytz
from dateutil.parser import parse

lock = threading.Lock()


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()  # работа с БД

    def checkRegister(self, base, name, forms):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM {base} WHERE {name} LIKE '{forms}'")
            if self.__cur.fetchone()['count'] > 0:
                print(f'Пользователь с таким {forms} уже существует. . .')
                return False
            else:
                return True
        except sqlite3.Error as e:
            print("Ошибка получения запроса в БД:\n" + str(e))
            return False

    def addUser(self, name, surname, email, login, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM lk WHERE user_email LIKE '{email}'")
            if self.__cur.fetchone()['count'] > 0:
                print('Пользователь с таким email уже существует. . .')
                return False
            tm = datetime.datetime.now(pytz.timezone('Europe/Moscow'))
            self.__cur.execute("INSERT INTO lk VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)",
                               (name, surname, email, login, hpsw, tm.strftime("%Y-%m-%d %H.%M.%S"), 'Участник', 0, 0,
                                False))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД:\n" + str(e))
            return False
        return True

    def getIDCount(self, arg):
        try:
            self.__cur.execute(f"SELECT COUNT(*) as `count` FROM '{arg}'")
            return self.__cur.fetchone()['count']
        except sqlite3.Error as e:
            print("Ошибка получения запроса в БД:\n" + str(e))
            return False

    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM lk WHERE ID = '{user_id}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД:\n" + str(e))
        return False

    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM lk WHERE user_email = '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД:\n" + str(e))
        return False

    def updateUserAvatar(self, avatar, user_id):
        if not avatar:
            return False
        try:
            binary = sqlite3.Binary(avatar)
            self.__cur.execute(f"UPDATE lk SET avatar = ? WHERE id = ?", (binary, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка обновления аватара в БД: " + str(e))
            return False
        return True

    def getContestInfo(self):
        try:
            _list_ = []
            self.__cur.execute(
                f"SELECT id, name_contest, time_contest, run_time, sql_db_user FROM contest WHERE run_time > "
                f"'{datetime.datetime.now(pytz.timezone('Europe/Moscow'))}' ORDER BY run_time")
            db_list = self.__cur.fetchall()
            num = 0
            for elem in db_list:
                for j in range(len(elem)):
                    _list_.append(elem[j])
                _list_.append(num)
                num += 1
            if _list_:
                return _list_
            return ['Not info in database']
        except sqlite3.Error as e:
            print("Ошибка в БД getContestInfo: " + str(e))
            return []

    def getContestInfoBegin(self):
        try:
            _list_ = []
            self.__cur.execute(
                f"SELECT id, name_contest, time_contest, end_time, sql_db_user FROM contest WHERE end_time > "
                f"'{datetime.datetime.now(pytz.timezone('Europe/Moscow'))}' and run_time <= "
                f"'{datetime.datetime.now(pytz.timezone('Europe/Moscow'))}' ORDER BY end_time")
            db_list = self.__cur.fetchall()
            num = 0
            for elem in db_list:
                for j in range(len(elem)):
                    _list_.append(elem[j])
                _list_.append(num)
                num += 1
            if _list_:
                return _list_
            return ['Not info in database']
        except sqlite3.Error as e:
            print("Ошибка в БД getContestInfo: " + str(e))
            return []

    def getContestInfo_all(self):
        try:
            _list_ = []
            self.__cur.execute(
                f"SELECT id, name_contest, time_contest, run_time, author, sql_db_user, div FROM contest WHERE run_time > "
                f"'{datetime.datetime.now(pytz.timezone('Europe/Moscow'))}' ORDER BY run_time")
            db_list = self.__cur.fetchall()
            num = 0
            for elem in db_list:
                for j in range(len(elem)):
                    if j == 3:
                        _list_.append([parse(elem[j]).strftime('%d-%m-%Y'), elem[j]])
                    else:
                        _list_.append(elem[j])
                _list_.append(num)
                num += 1
            if _list_:
                return _list_
            return ['Not info in database']
        except sqlite3.Error as e:
            print("Ошибка в БД getContestInfo_all: " + str(e))
            return ['Error']

    def getContestInfo_all_begin(self):
        try:
            _list_ = []
            self.__cur.execute(
                f"SELECT id, name_contest, time_contest, run_time, author, sql_db_user, div, end_time FROM contest "
                f"WHERE run_time <= "
                f"'{datetime.datetime.now(pytz.timezone('Europe/Moscow'))}' and end_time >= "
                f"'{datetime.datetime.now(pytz.timezone('Europe/Moscow'))}' ORDER BY "
                f"run_time")
            db_list = self.__cur.fetchall()
            num = 0
            for elem in db_list:
                for j in range(len(elem)):
                    _list_.append(elem[j])
                _list_.append(num)
                num += 1
            if _list_:
                return _list_
            return [0, 'Not info in database']
        except sqlite3.Error as e:
            print("Ошибка в БД getContestInfo_all_begin: " + str(e))
            return False

    def updateUser(self, name, surname, login, user_id):
        try:
            self.__cur.execute(f"UPDATE lk SET user_name = ?, user_surname = ?, user_login = ? WHERE id = ?",
                               (name, surname, login, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка обновления данных пользователя в БД: " + str(e))
            return False
        return True

    def getUserRankAll(self):
        try:
            self.__cur.execute(f"SELECT rating, user_login FROM lk ORDER BY rating LIMIT 10")
            _ds_ = self.__cur.fetchall()
            _list_ = []
            for elem in _ds_:
                for j in range(len(elem)):
                    _list_.append(elem[j])
            _dict_ = dict()
            j = 0
            for i in range(0, len(_list_), 2):
                j += 1
                _dict_[_list_[i + 1]] = [_list_[i], j]
            return _dict_
        except sqlite3.Error as e:
            print("Ошибка получения рейтинга в БД: " + str(e))
            return {'NaN': 'NaN'}

    def getUserTaskAll(self):
        try:
            self.__cur.execute(f"SELECT task, user_login FROM lk ORDER BY rating LIMIT 10")
            _ds_ = self.__cur.fetchall()
            _list_ = []
            for elem in _ds_:
                for j in range(len(elem)):
                    _list_.append(elem[j])
            _dict_ = dict()
            j = 0
            for i in range(0, len(_list_), 2):
                j += 1
                _dict_[_list_[i + 1]] = [_list_[i], j]
            return _dict_
        except sqlite3.Error as e:
            print("Ошибка получения рейтинга в БД: " + str(e))
            return {'NaN': 'NaN'}

    def getBlog(self):
        try:
            self.__cur.execute(f"SELECT * FROM blog")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения blog в БД: " + str(e))
            return ('NaN', 'NaN', 'NaN 00:00:00', '0')

    def addPostDB(self, arg1, arg2, arg3, status, user_id, arv1=None):
        try:
            self.__cur.execute("INSERT INTO blog VALUES(NULL, ?, ?, ?, ?, ?, ?, 'NOT_MODERATE', ?)",
                               (arg1, arg2, arg3,
                                datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime(
                                    '%Y-%m-%d %H:%M:%S'),
                                arv1, status, user_id))
            self.__db.commit()
            return True
        except sqlite3.Error as e:
            print("Ошибка сохранения blog в addPostDB: " + str(e))
            return False

    def getPost(self, postId):
        try:
            self.__cur.execute(f"SELECT author, timestamp, title, content FROM blog WHERE id = {postId}")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи is getPost " + str(e))

        return (False, False)

    def getPostsAnonce(self, count=None):
        try:
            self.__cur.execute(f"SELECT id, title, announce, content, timestamp FROM blog  WHERE status = 'global' "
                               f"ORDER BY timestamp DESC LIMIT {count}")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из getPostsAnonce " + str(e))

        return []

    def getInformation(self, visual):
        try:
            self.__cur.execute(f"SELECT type, text FROM information  WHERE status = 1 AND visual = '{visual}'")
            _list_ = self.__cur.fetchall()
            _dict_ = dict()
            for elem in _list_:
                _dict_[elem[0]] = elem[1]
            return _dict_
        except sqlite3.Error as e:
            print("Ошибка получения информации из getInformation " + str(e))
        return []

    def getLogin(self, us_id):
        try:
            lock.acquire(True)
            self.__cur.execute(f"SELECT user_login FROM lk WHERE ID = '{us_id}'")
            res = self.__cur.fetchone()
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из getLogin:\n" + str(e))
        finally:
            lock.release()
        return False

    def get_contest_name(self, cont_id):
        try:
            self.__cur.execute(f"SELECT sql_db_user FROM contest WHERE id = '{cont_id}'")
            res = self.__cur.fetchone()
            return res[0]
        except sqlite3.Error as e:
            print("Ошибка получения данных из get_contest_name:\n" + str(e))
        return 'NaN'

    def contest_run_time(self, contest_id):
        try:
            self.__cur.execute(f"SELECT run_time FROM contest WHERE id = '{contest_id}'")
            res = self.__cur.fetchone()
            print(parse(*res), datetime.datetime.now(pytz.timezone('Europe/Moscow')))
            if parse(*res) <= datetime.datetime.now(pytz.timezone('Europe/Moscow')):
                return True
            return False
        except sqlite3.Error as e:
            print("Ошибка получения данных из contest_run_time:\n" + str(e))
        return False

    def bool_get_contest_id_is_used(self, contest_id):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM contest WHERE id LIKE '{contest_id}'")
            if self.__cur.fetchone()['count'] > 0:
                return True
            return False
        except sqlite3.Error as e:
            print('Ошибка в bool_get_contest_id_is_used:', e)
            return False

    def get_contest_run_time(self, contest_id):
        try:
            self.__cur.execute(f"SELECT run_time FROM contest WHERE id = '{contest_id}'")
            res = self.__cur.fetchone()
            return res[0]
        except sqlite3.Error as e:
            print("Ошибка получения данных из contest_run_time:\n" + str(e))
        return 'NaN'

    def get_task(self, contest_id):
        try:
            self.__cur.execute(f"SELECT sql_db_task FROM contest WHERE id = '{contest_id}'")
            ans = self.__cur.fetchone()
            return ans
        except sqlite3.Error as e:
            print("Ошибка получения данных из get_task:\n" + str(e))
        return False

    def get_format_of_contest(self, contest_id):
        try:
            self.__cur.execute(f"SELECT format FROM contest WHERE id = '{contest_id}'")
            ans = self.__cur.fetchone()
            return ans
        except sqlite3.Error as e:
            print("Ошибка получения данных из get_format_of_contest:\n" + str(e))
        return False
