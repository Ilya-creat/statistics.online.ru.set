# app.py
from werkzeug.middleware.dispatcher import \
    DispatcherMiddleware  # use to combine each Flask app into a larger one that is dispatched based on prefix

from BACKEND.app import application as app
from BACKEND.API.api_run import application as app_api

app.wsgi_app = DispatcherMiddleware(app.wsgi_app,
                                   {
                                       '/api': app_api.wsgi_app
                                   })
