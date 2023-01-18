from flask import url_for
from flask_login import UserMixin


class UserLogin(UserMixin):
    def fromDB(self, user_id, db):
        self.__user = db.getUser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['id'])

    def get_name(self):
        return str(self.__user['user_name'])

    def get_surname(self):
        return str(self.__user['user_surname'])

    def get_login(self):
        return str(self.__user['user_login'])

    def get_status(self):
        return str(self.__user['status'])

    def get_rating(self):
        return str(self.__user['rating'])

    def get_avatar(self, app):
        img = None
        if not self.__user['avatar']:
            try:
                with app.open_resource(app.root_path + url_for('static', filename='lk/img/default.png'), "rb") as f:
                    img = f.read()
            except FileNotFoundError as e:
                print('Аватарка по умолчанию не найдена:' + str(e))
        else:
            img = self.__user['avatar']
        return img

    def verifyExt(self, filename):
        ext = filename.rsplit('.', 1)[1]
        if ext.lower() == 'png' or ext.lower() == 'jpg' or ext.lower() == 'gif' or ext.lower() == 'jpeg':
            return True

        return False
