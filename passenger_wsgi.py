import sys

import os

INTERP = os.path.expanduser("/var/www/u1936728/data/flaskenv/bin/python")
if sys.executable != INTERP:
   os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.getcwd())

from BACKEND.API.api_run import application
from werkzeug.debug import DebuggedApplication
# Опционально: подключение модуля отладки

application.wsgi_app = DebuggedApplication(application.wsgi_app, True)
# Опционально: включение модуля отадки

application.wsgi_app.debug = True
# Опционально: True/False устанавливается по необходимости в отладке