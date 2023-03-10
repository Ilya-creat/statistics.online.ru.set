import os
import sqlite3
from datetime import timedelta

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
import BACKEND.API.resources
from flask_cors import CORS, cross_origin

application = Flask(__name__)
api = Api(application)
cors = CORS(application)
application.config['CORS_HEADERS'] = 'Content-Type'
application.config['JWT_SECRET_KEY'] = '67C21E473EEB3FBB87D3C2F3E71B7-8E9D5F6DFC7762F4412C2D682CA59' \
                                   '-FE28CA1BAFDA84126E173ABE2AE44 '
jwt = JWTManager(application)
application.config['JWT_BLACKLIST_ENABLED'] = True
application.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
application.permanent_session_lifetime = timedelta(days=365)
api.add_resource(BACKEND.API.resources.Info, '/')

# API 1.0
api.add_resource(BACKEND.API.resources.InfoApiVersion, '/api-v1.0')
api.add_resource(BACKEND.API.resources.UserLogin, '/api-v1.0/authorization/login')
api.add_resource(BACKEND.API.resources.UserRegistration, '/api-v1.0/authorization/register')
api.add_resource(BACKEND.API.resources.UserLogoutAccess, '/api-v1.0/logout/access')
api.add_resource(BACKEND.API.resources.UserLogoutRefresh, '/api-v1.0/logout/refresh')
api.add_resource(BACKEND.API.resources.TokenRefresh, '/api-v1.0/token/refresh')
api.add_resource(BACKEND.API.resources.AllUsers, '/api-v1.0/users')
api.add_resource(BACKEND.API.resources.CheckedSession, '/api-v1.0/checked-session')
api.add_resource(BACKEND.API.resources.GetUserInfo, '/api-v1.0/get-user-info')
api.add_resource(BACKEND.API.resources.Picture, '/api-v1.0/image/users')


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(self, decrypted_token):
    return BACKEND.API.resources.global_sql.check_if_token_in_blacklist(decrypted_token['jti'])


if __name__ == '__main__':
    application.run(host='localhost', port=5000, debug=False, threaded=True)
