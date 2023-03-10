from werkzeug.serving import run_simple
from BACKEND.sf import app

application = app

if __name__ == '__main__':
    run_simple('localhost', 5000, application, use_reloader=True, use_debugger=True, use_evalex=True)