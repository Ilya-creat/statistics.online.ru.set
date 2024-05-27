import os
import sqlite3

from flask import make_response, jsonify
from flask_restful import Resource, reqparse
from werkzeug.security import generate_password_hash, check_password_hash
from BACKEND.API.sql import SQL
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from BACKEND.Models.functions import is_valid_password, check_email, is_valid_login

parser_login = reqparse.RequestParser()
parser_login.add_argument('token', help='-', required=True)
parser_login.add_argument('login', help='Данный параметр не заполнен!', required=True)
parser_login.add_argument('password', help='Данный параметр не заполнен!', required=True)

parser_reg = reqparse.RequestParser()
parser_reg.add_argument('token', help='-', required=True)
parser_reg.add_argument('login', help='Данный параметр не заполнен!', required=True)
parser_reg.add_argument('email', help='Данный параметр не заполнен!', required=True)
parser_reg.add_argument('telephone', help='Данный параметр не заполнен!', required=True)
parser_reg.add_argument('password_1', help='Данный параметр не заполнен!', required=True)
parser_reg.add_argument('password_2', help='Данный параметр не заполнен!', required=True)

data_client = reqparse.RequestParser()
data_client.add_argument('token', help='-', required=True)
db = None
if 'API' in os.getcwd():
    db = sqlite3.Connection(f"{os.getcwd()}/../database.db", check_same_thread=False)
else:
    db = sqlite3.Connection(f"/var/www/statistics_online/BACKEND/database.db", check_same_thread=False)
db.row_factory = sqlite3.Row
global_sql = SQL(db)


class Info(Resource):
    def post(self):
        response = jsonify({
            'http_code': 200,
            'status': "ok",
            'info': 'statistics-online-api'
        })
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    def get(self):
        response = jsonify({
            'http_code': 200,
            'status': "ok",
            'info': 'statistics-online-api'
        })
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response


class InfoApiVersion(Resource):
    def post(self):
        response = jsonify({
            'http_code': 200,
            'status': "ok",
            'version': '1.0',
            'info': 'statistics-online-api'
        })
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    def get(self):
        response = jsonify({
            'http_code': 200,
            'status': "ok",
            'version': '1.0',
            'info': 'statistics-online-api'
        })
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response


class UserRegistration(Resource):
    def __init__(self):
        self._db = db
        self.sql_ = SQL(self._db)

    def post(self):
        data = parser_reg.parse_args()
        if not self.sql_.check_secret_key(data["token"]):
            response = make_response(jsonify({
                       'http_code': 403,
                       'status': "unavailable-api",
                       'message': 'api token not is correct',
                       'type': 'api',
                       'message-ru': 'Ошибка приложения.',
                       'message-en': 'Application Error.'}), 403)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
        if not is_valid_login(data["login"]):
            response = make_response(jsonify({
                       'http_code': 403,
                       'status': "unavailable",
                       'message': 'incorrect data',
                       'type': 'login',
                       'message-ru': 'Логин не соответствует требованиям.',
                       'message-en': 'Login does not meet the requirements.'}), 403)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
        if not check_email(data["email"]):
            response = make_response(jsonify({
                       'http_code': 403,
                       'status': "unavailable",
                       'message': 'incorrect data',
                       'type': 'email',
                       'message-ru': 'Неверный EMAIL.',
                       'message-en': 'Invalid EMAIL.'}), 403)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
        if data["password_1"] != data["password_2"]:
            response = make_response(jsonify({
                       'http_code': 403,
                       'status': "unavailable",
                       'message': 'wrong credentials',
                       'type': 'psw_incorrect',
                       'message-ru': 'Пароли не совпадают.',
                       'message-en': 'Passwords don\'t match.'}), 403)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
        if not is_valid_password(data["password_1"]):
            response = make_response(jsonify({
                       'http_code': 403,
                       'status': "unavailable",
                       'message': 'incorrect data',
                       'type': 'psw_security',
                       'message-ru': 'Пароль ненадежный.',
                       'message-en': 'The password is unreliable.'}), 403)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response

        ans = self.sql_.addUser_api(data["login"], data["telephone"], data["email"],
                                    generate_password_hash(data["password_1"]))
        if ans["error"] == "ok":
            access_token = create_access_token(identity=self.sql_.get_user_id(data['login'])['ID'])
            refresh_token = create_refresh_token(identity=self.sql_.get_user_id(data['login'])['ID'])
            response = make_response(jsonify({
                       'http_code': 200,
                       'status': "available",
                       'message': f'Logged in as {data["login"]}',
                       'message-ru': 'Регистрируем и входим...',
                       'message-en': 'We enter...',
                       'access_token': access_token,
                       'refresh_token': refresh_token
                   }), 403)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
        else:
            if ans["error"] == "email":
                response = make_response(jsonify({
                           'http_code': 403,
                           'status': "unavailable",
                           'message-system': 'registration failed',
                           'type': 'email',
                           'message-ru': 'Пользователь с таким EMAIL уже существует.',
                           'message-en': 'A user with this EMAIL already exists.'}), 403)
                response.headers.add("Access-Control-Allow-Origin", "*")
                return response
            elif ans["error"] == "login":
                response = make_response(jsonify({
                           'http_code': 403,
                           'status': "unavailable",
                           'message-system': 'registration failed',
                           'type': 'login',
                           'message-ru': 'Пользователь с таким LOGIN уже существует.',
                           'message-en': 'A user with this LOGIN already exists.'}), 403)
                response.headers.add("Access-Control-Allow-Origin", "*")
                return response
            elif ans["error"] == "telephone":
                response = make_response(jsonify({
                           'http_code': 403,
                           'status': "unavailable",
                           'message-system': 'registration failed',
                           'type': 'telephone',
                           'message-ru': 'Пользователь с таким телефоном уже существует.',
                           'message-en': 'A user with this telephone already exists.'}), 403)
                response.headers.add("Access-Control-Allow-Origin", "*")
                return response
            response = make_response(jsonify({
                       'http_code': 500,
                       'status': "unavailable",
                       'message-system': 'registration failed',
                       'type': None,
                       'message-ru': 'Системная ошибка. Повторите запрос позже.',
                       'message-en': 'System error. Repeat the request later.'}), 500)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response


class UserLogin(Resource):
    def __init__(self):
        self._db = db
        self.sql_ = SQL(self._db)

    def post(self):
        data = parser_login.parse_args()
        if not self.sql_.check_secret_key(data["token"]):
            response = make_response(jsonify({
                       'http_code': 403,
                       'status': "unavailable-api",
                       'message': 'api token not is correct',
                       'type': 'api',
                       'message-ru': 'Ошибка приложения',
                       'message-en': 'Application Error'}), 403)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
        user = None
        if self.sql_.getUserByEmail(data["login"]):
            user = self.sql_.getUserByEmail(data["login"])
        if self.sql_.getUserByLogin(data["login"]):
            user = self.sql_.getUserByLogin(data["login"])
        if self.sql_.getUserByTelephone(data["login"]):
            user = self.sql_.getUserByTelephone(data["login"])
        if user and check_password_hash(user['user_psw'], data["password"]):
            # print(self.sql_.get_user_id(data['login'])['ID'])
            access_token = create_access_token(identity=self.sql_.get_user_id(data['login'])['ID'])
            refresh_token = create_refresh_token(identity=self.sql_.get_user_id(data['login'])['ID'])
            response = jsonify({
                'http_code': 200,
                'status': "available",
                'message': f'Logged in as {user["user_login"]}',
                'message-ru': 'Входим...',
                'message-en': 'We enter...',
                'access_token': access_token,
                'refresh_token': refresh_token
            })
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
        else:
            response = make_response(jsonify({
                       'http_code': 403,
                       'status': "unavailable",
                       'message-system': 'wrong credentials',
                       'type': 'authorization',
                       'message-ru': 'Неверный логин или пароль.',
                       'message-en': 'Invalid username or password.'}), 403)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response

    def get(self):
        response = jsonify({
            'http_code': 200,
            'status': 'ok'
        })
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response


class UserLogoutAccess(Resource):
    def __init__(self):
        self._db = db
        self.sql_ = SQL(self._db)

    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        try:
            self.sql_.add_token(jti)
            response = jsonify({
                'http_code': 200,
                'message': 'Access token has been revoked'})
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
        except:
            response = make_response(jsonify({
                       'http_code': 500,
                       'message': 'Something went wrong'}), 500)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response


class UserLogoutRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        jti = get_jwt()['jti']
        try:
            self.sql_.add_token(jti)
            response = jsonify({
                'http_code': 200,
                'message': 'Refresh token has been revoked'})
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
        except:
            response = make_response(jsonify({
                       'http_code': 500,
                       'message': 'Something went wrong'}), 500)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response


class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        response = jsonify({
            'http_code': 200,
            'access_token': access_token
        })
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response


class AllUsers(Resource):
    def get(self):
        response = jsonify({
            'http_code': 200,
            'message': 'List of users'
        })
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    def delete(self):
        response = jsonify({
            'http_code': 200,
            'message': 'Delete all users'
        })
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response


class CheckedSession(Resource):
    @jwt_required()
    def get(self):
        response = jsonify({
            'http_code': 200,
            'status': 'ok'
        })
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response


class GetUserInfo(Resource):
    def __init__(self):
        self._db = db
        self.sql_ = SQL(self._db)

    @jwt_required()
    def get(self):
        data = data_client.parse_args()
        # print(data["token"])
        if not self.sql_.check_secret_key(data["token"]):
            response = make_response(jsonify({
                       'http_code': 403,
                       'status': "unavailable-api",
                       'message': 'api token not is correct',
                       'type': 'api',
                       'message-ru': 'Ошибка приложения.',
                       'message-en': 'Application Error.'}), 403)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
        user_id = get_jwt_identity()
        user_info = self.sql_.get_user_info(user_id)
        response = jsonify({
            "http_code": 200,
            "message": "get user info",
            "user-info": {
                "name": user_info["user_name"],
                "surname": user_info["user_surname"],
                "email": user_info["user_email"],
                "login": user_info["user_login"],
                "user_telephone": user_info["user_num"],
                "time_reg": user_info["time_reg"],
                "status": user_info["status"],
                "rating": user_info["rating"],
                "task": user_info["task"],
                "admin_role": user_info["admin_role"],
                "avatar": f'https://u1936728.isp.regruhosting.ru/api/api-v1.0/image/users?pid={user_id}&token={data["token"]}'
            }
        })
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response


class Picture(Resource):
    def __init__(self):
        self._db = db
        self.sql_ = SQL(self._db)

    @jwt_required()
    def get(self):
        data = data_client.parse_args()
        # print(data["token"])
        if not self.sql_.check_secret_key(data["token"]):
            response = make_response(jsonify({
                       'http_code': 403,
                       'status': "unavailable-api",
                       'message': 'api token not is correct',
                       'type': 'api',
                       'message-ru': 'Ошибка приложения.',
                       'message-en': 'Application Error.'}), 403)
            response.headers.add("Access-Control-Allow-Origin", "*")
            return response
        user_id = get_jwt_identity()
        user_info = self.sql_.get_user_info(user_id)
        img = user_info["avatar"]
        if not img:
            return 'НЕТ'
        h = make_response(img)
        h.headers.set('Content-Type', 'image/jpeg')
        h.headers.set(
            'Content-Disposition', 'attachment', filename='%s.jpg' % user_id)
        h.headers.add("Access-Control-Allow-Origin", "*")
        return h
