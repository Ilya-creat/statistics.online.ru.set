import json
import os
import sqlite3
import threading
from ast import literal_eval
from datetime import datetime

import pytz
import requests
from flask import Flask, render_template, url_for, redirect, g, flash, request, make_response, \
    abort
from flask_ckeditor import CKEditor
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from BACKEND.Models.FDataBase import FDataBase
from BACKEND.Models.FDataBase_Task import Contest_SQL
from BACKEND.Models.Forms import LoginForm, RegisterForm
from BACKEND.Models.UserLogin import UserLogin
import urllib3

# Config
DEBUG = False
SECRET_KEY = '5PAy8Kzr-cyMTeYAYPDL97ZUrBDpNcMhFQ2k_am_G0XHHcN9O7i0GTCKuz83k' \
             'STFGUCEtcLBacUchaQbps5UmrGei5foFuKWIc4UUqbL4PyOz473BrJhdGw16CEFymABLm5Ezw'
application = Flask(__name__, subdomain_matching=True,
                    static_folder='../WEB/static',
                    template_folder='../WEB/templates')
application.config.from_object(__name__)  # load configuration
application.config.update(dict(DATABASE=os.path.join(application.root_path, 'database.db')))  # переопределине пути к БД
application.config['MAX_CONTENT_LENGTH'] = 2048 * 2048
uploads_dir = os.path.join(application.instance_path, 'post_files')
REMEMBER_COOKIE_DOMAIN = False
login_manager = LoginManager(application)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для просмотра данной странички"
login_manager.login_message_category = "error"
ckeditor = CKEditor(application)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'csv'}
compiler = {'python3': 'Python 3.10', 'pypy3': 'Pypy 3.9', 'gcc': 'GCC C 12.2',
            'gnu20': 'GNU C++ 20', 'java17': 'Java 17', 'js9': 'JavaScript 9', 'freepascal': 'Free Pascal 3.0.4'}
url_ = 'https://ca90-79-139-157-192.eu.ngrok.io'  # https://statistics-online.ru | https://localhost:5000
url_server = 'https://f28e-79-139-157-192.eu.ngrok.io'  # https://server.statistics-online.ru | https://localhost:5001

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


##################################################################################################
def index(list_olimp_post, size_post, begin, interval):
    _list_ = []

    for i in range(begin, size_post, interval):
        reg_user = contest_task_base.user_login_contest(current_user.get_id(), list_olimp_post[i])
        if reg_user:
            _list_.append(True)
        else:
            _list_.append(False)
    return _list_


def login_contest(id_contest):
    contest_sql = dbase.get_contest_name(id_contest)
    user_verifi = contest_task_base.user_login_contest(current_user.get_id(), contest_sql)
    print((user_verifi and dbase.contest_run_time(id_contest)) or \
          (user_verifi and contest_task_base.get_status_active(contest_sql, current_user.get_id())))
    if (user_verifi and dbase.contest_run_time(id_contest)) or \
            (user_verifi and contest_task_base.get_status_active(contest_sql, current_user.get_id())):
        return True
    return False


def contest_verifi_id(id_contest):
    if dbase.bool_get_contest_id_is_used(id_contest):
        return True
    else:
        return False


def get_login_author(_list_, inter1, inter2):
    for i in range(inter1, len(_list_), inter2):
        pb = []
        # print(literal_eval(_list_[i]))
        for j in literal_eval(_list_[i]):
            if dbase.getLogin(j):
                pb.append(*dbase.getLogin(j))
        _list_[i] = pb
    return _list_


##################################################################################################


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    conn = sqlite3.connect(application.config['DATABASE'], check_same_thread=False)
    conn.row_factory = sqlite3.Row  # преобразование в вид: словарей
    return conn


def conn_db_un_appconfig():
    conn = sqlite3.connect(os.path.join(application.root_path, 'contest.db'), check_same_thread=False)
    conn.row_factory = sqlite3.Row  # преобразование в вид: словарей
    return conn


def create_db():
    """Вспомогательная функция создания таблиц БД"""
    db = connect_db()
    with application.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    """Соединение с БД, если оно еще не установлено"""
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


def get_db_two():
    if not hasattr(g, 'link_db_contest'):
        g.link_db_contest = conn_db_un_appconfig()
    return g.link_db_contest


dbase = None
contest_task_base = None


@application.before_request
def before_request():
    """Установление соединение с БД перед выполнения запроса"""
    global dbase
    global contest_task_base
    db = get_db()
    db_contest = get_db_two()
    dbase = FDataBase(db)
    contest_task_base = Contest_SQL(db_contest)


@application.teardown_appcontext
def close_db(error):
    """Закрываем соединение с БД, если оно было установлено"""
    if hasattr(g, 'link_db_contest'):
        g.link_db_contest.close()


@application.route('/')
def main():
    if current_user.is_authenticated:
        _list_ = dbase.getContestInfo()
        # print(*_list_)
        contest_ans = index(_list_, len(_list_), 4, 6)
        _list_begin_ = dbase.getContestInfoBegin()
        # print(*_list_begin_)
        _list_b_ = index(_list_begin_, len(_list_begin_), 4, 6)

        rank_list = dbase.getUserRankAll()
        # print(rank_list)
        task_list = dbase.getUserTaskAll()
        warn = dbase.getInformation('online')
        return render_template('lk/main.html',
                               header="Statistics.Online",
                               text_button="Продолжим?",
                               title="Statistics.Online",
                               text="Привет, {a} !".format(a=current_user.get_name()),
                               header_map={'Соревнования': '/list',
                                           'Библиотека': '/library/main',
                                           'Профиль': '/profile/' +
                                                      current_user.get_id(),
                                           'FAQ': '/faq'},
                               ID_user=dbase.getIDCount('lk'),
                               ID_server=dbase.getIDCount('server'),
                               _list_contest_=_list_,
                               reg_user=contest_ans,
                               contest_list_begin=_list_begin_,
                               reg_user_begin=_list_b_,
                               list_rank=rank_list,
                               list_task=task_list,
                               posts=dbase.getPostsAnonce(10),
                               warn=warn,
                               MSKTIME=datetime.now(pytz.timezone('Europe/Moscow')).strftime('%H:%M:%S'))
    return render_template('main.html',
                           header="Statistics.Online",
                           text_button="Приступим",
                           title="Statistics.Online",
                           text="Новый проект по программированию!",
                           header_map={'Преимущество': 'stat', 'FAQ': 'faq'},
                           ID_user=dbase.getIDCount('lk'),
                           ID_server=dbase.getIDCount('server'),
                           MSKTIME=datetime.now(pytz.timezone('Europe/Moscow')).strftime('%H:%M:%S'))


@application.route('/faq')
def faq():
    return render_template("faq.html",
                           header="Statistics.Online",
                           title="Statistics | FAQ",
                           top_title="Statistics | FAQ",
                           top_title_h3="Здесь собраны актуальные вопросы!",
                           header_map={'На главную': '/'})


@application.route('/login', methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(f'/profile/{current_user.get_id()}')

    form_log = LoginForm()
    form_reg = RegisterForm()
    if form_log.validate_on_submit():
        user = dbase.getUserByEmail(form_log.email.data)
        if user and check_password_hash(user['user_psw'], form_log.psw.data):
            userlogin = UserLogin().create(user)
            rm = form_log.remember.data
            login_user(userlogin, remember=rm)
            return redirect(request.args.get('next') or '/')

        flash('Неверный Email или пароль!', category='error')

    return render_template('lk/loginforms.html',
                           form_reg=form_reg,
                           form_log=form_log,
                           header="Statistics.Online",
                           title="Statistics.Online",
                           header_map={'На главную': '/'})


@application.route('/register', methods=["POST", "GET"])
def register():
    form_reg = RegisterForm()
    form_log = LoginForm()
    if form_reg.validate_on_submit():
        a = dbase.checkRegister('lk', 'user_email', form_reg.email.data)
        b = dbase.checkRegister('lk', 'user_login', form_reg.login.data)
        if not a:
            flash('Пользователь с таким EMAIL уже существует!', category='error')
            return redirect('/login')
        elif not b:
            flash('Пользователь с таким Login уже существует!', category='error')
            return redirect('/login')
        res = dbase.addUser(form_reg.name.data, form_reg.surname.data, form_reg.email.data,
                            form_reg.login.data, generate_password_hash(form_reg.psw1.data))
        if res:
            flash('Вы успешно зарегистрировались', category='success')
            return redirect('/login')
    else:
        flash('Произошла ошибка при регистрации! Вернитесь в форму регистрации и проверте корректность данных!',
              category='error')
    return render_template('lk/loginforms.html',
                           form_reg=form_reg,
                           form_log=form_log,
                           header="Statistics.Online",
                           title="Statistics.Online",
                           header_map={'На главную': '/'})


@application.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    if str(user_id) != current_user.get_id():
        return render_template('errors_pages/error_base.html',
                               number_error='S23',
                               number_error_len=3,
                               text_problem='У вас нет прав к просмотру данной страницы!',
                               _list_={'В свой профиль': '/profile/{user_id}'.format(user_id=current_user.get_id())},
                               title="Statistics.Online")
    return render_template("lk/profile.html",
                           header="Statistics.Online",
                           title="Profile",
                           header_map={'Главная': '/', ' Выйти из профиля': '/logout'},
                           id=current_user.get_id(),
                           meaning=current_user.get_status(),
                           name=current_user.get_name(),
                           surname=current_user.get_surname(),
                           login=current_user.get_login(),
                           rating=current_user.get_rating(),
                           profile_values={'Блог': '/post/list', 'Друзья': f'profile/{current_user.get_id()}/friends',
                                           'Прогресс': f'profile/{current_user.get_id()}/rank'}
                           )


@application.route('/user_ava')
@login_required
def user_ava():
    img = current_user.get_avatar(application)
    if not img:
        return 'НЕТ'
    h = make_response(img)
    return h


def allowed_file(filename):
    """ Функция проверки расширения файла """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@application.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            if allowed_file(file.filename):
                # print(allowed_file(file.filename))
                try:
                    img = file.read()
                    res = dbase.updateUserAvatar(img, current_user.get_id())
                    if not res:
                        flash('Ошибка обновления аватра', 'error')
                    flash('Аватар обновлен', 'success')
                except FileNotFoundError as e:
                    flash('Ошибка чтения аватра', 'error')
            else:
                flash('Недопустимый формат файла! Возможно использовать'
                      '(.png, .jpg, .gif, .csv, .jpeg)', 'error')
        else:
            flash('Ошибка обновления аватра', 'error')

    return redirect(f'profile/{current_user.get_id()}')


@application.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта', category='success')
    return redirect(url_for('login'))


@application.route('/reg/<path:__type__>', methods=["POST", "GET"])
def reg(__type__):
    if __type__ == "user_contest":
        contest_dbase = request.args.get('contest_user_dbase')
        _verefi_ = contest_task_base.checkRegister(contest_dbase, 'USER_ID', current_user.get_id())
        if not _verefi_:
            flash('Вы уже зарегистрированы на турнир!', category='info')
            return redirect('/list')
        n = contest_task_base.reg_user_in_dbase(contest_dbase, current_user.get_id())
        if n:
            flash('Вы успешно зарегистрированы на турнир!', category='success')
        else:
            flash('Ошибка регистрирования. . .', 'error')
        return redirect('/list')
    if __type__ == "profile":
        _verefi_ = dbase.checkRegister('lk', 'user_login', request.form.get('login'))
        if not _verefi_ and request.form.get('login') != current_user.get_login():
            flash('Пользователь с таким логином существует!', category='error')
            return redirect(f'/profile/{current_user.get_id()}#okno_black')
        _add_ = dbase.updateUser(request.form.get('name'), request.form.get('surname'), request.form.get('login'),
                                 current_user.get_id())
        if _add_:
            flash('Вы успешно изменили данные!', category='success')
            return redirect(f'/profile/{current_user.get_id()}#close')
        else:
            flash('Произошла ошибка при обновлении данных! Повторите операцию позже.', category='error')
            return redirect(f'/profile/{current_user.get_id()}#close')


@application.route('/result/test')
def resultMM():
    return render_template('result/CR1.htm',
                           title='Statistics.Online')


@application.route('/<__type__>')
@login_required
def contest(__type__):
    if __type__ == 'crash':
        return render_template('errors_pages/error_base.html',
                               number_error='S05',
                               number_error_len=3,
                               text_problem='Дорогой участник! К сожалению платформа переполнена запросами от серверов!'
                                            'Просим вас воспользоваться следующими резервными платформами:',
                               list={'m1.statistics-platform.ru': '/',
                                     'На главную': '/'},
                               title="Statistics.Error")
    if __type__ == 'list':
        _list_ = dbase.getContestInfo_all()
        _list_ = get_login_author(_list_, 4, 8)
        reg_success_user = contest_task_base.getContestInfo_all_count(_list_, 5, 8)
        contest_ans = index(_list_, len(_list_), 5, 8)
        _list_begin_ = dbase.getContestInfo_all_begin()
        _list_begin_ = get_login_author(_list_begin_, 4, 9)
        _list_b_ = index(_list_begin_, len(_list_begin_), 5, 9)
        contest_begin = contest_task_base.getContestInfo_all_count(_list_begin_, 5, 9)
        # print(_list_)
        return render_template('statistics_olimp/'
                               'list_of_contests.html',
                               header='Statistics.Contest',
                               header_map={'Обратно': '/',
                                           'Архив задач': '/archive',
                                           'Профиль': f'/profile/{current_user.get_id()}'},
                               contest_list=_list_,
                               reg_user=contest_ans,
                               reg_success=reg_success_user,
                               contest_list_begin=_list_begin_,
                               reg_user_begin=_list_b_,
                               reg_begin=contest_begin,
                               url_=url_,
                               title="Statistics.Online")

    if __type__ == 'olimp':
        return render_template('statistics_olimp/olimp.html',
                               header='Statistics.Contest',
                               header_map={'На главную': '/',
                                           'Все соревнования': '/list',
                                           'Профиль': f'/profile/{current_user.get_id()}'},
                               title="Statistics.Online"
                               )
    if __type__ == 'archive':
        return render_template('errors_pages/error_base.html',
                               number_error='S05',
                               number_error_len=3,
                               text_problem='Дорогой участник! К сожалению платформа переполнена запросами от серверов!'
                                            'Просим вас воспользоваться следующими резервными платформами:',
                               list={'m1.statistics-platform.ru': '/',
                                     'На главную': '/'},
                               title="Statistics.Online")


@application.route("/time", methods=["GET", "POST"])
def time_contest_user():
    arg = request.args.get('contest')
    if not contest_verifi_id(arg):
        flash(f'Контеста {arg} не существует!', 'warning')
        return redirect('/contest/list')
    return render_template('lk/time.html',
                           header='Statistics.Time',
                           header_map={'Обратно': '/list'},
                           time_system=dbase.get_contest_run_time(arg),
                           user_local_time=dbase.get_contest_run_time(arg)
                           )


@application.route("/post/list")
def post_index():
    return render_template('lk/blog_list.html', posts=dbase.getPostsAnonce())


@application.route("/new_post")
def new_post():
    return render_template('lk/add_post.html',
                           header='Statistics.Editor',
                           header_map={'Обратно': '/'},
                           title="Statistics.Online"
                           )


@application.route("/post/<int:id_post>")
def showPost(id_post):
    author, timestamp, title, post_state = dbase.getPost(id_post)
    if not title:
        abort(404)
    return render_template('lk/blog.html', post=post_state, ctitle=title, author=dbase.getLogin(author)[0],
                           timestamp=timestamp,
                           header='Statistics.Online',
                           header_map={'Все новости': '/post/list',
                                       'На главную': '/'},
                           title="Statistics.Online")


@application.route("/add_post", methods=["POST", "GET"])
def addPost():
    if request.method == "POST":
        if len(request.form['title']) >= 4 and len(request.form['content']) >= 25 and len(
                request.form['announce']) >= 4:
            res = False
            if request.form['enter'] == 'Опубликовать':
                res = dbase.addPostDB(request.form['title'], request.form['announce'], request.form['content'],
                                      'user', current_user.get_id())
                flash('Статья добавлена успешно', category='success')
            elif request.form['enter'] == 'Сохранить как черновик':
                res = dbase.addPostDB(request.form['title'], request.form['announce'], request.form['content'],
                                      'local', current_user.get_id())
                flash('Статья добавлена успешно', category='success')
            if not res:
                if len(request.form['title']) < 4:
                    flash('Ошибка добавления статьи: длина символов в названии меньше 4', category='error')
                elif len(request.form['announce']) < 4:
                    flash('Ошибка добавления статьи: длина символов в анонсе меньше 4', category='error')
                else:
                    flash('Ошибка добавления статьи: длина символов в записи меньше 25', category='error')
        else:
            flash('Ошибка добавления статьи:', category='error')
    else:
        flash('Ошибка добавления статьи', category='error')

    return redirect(f'/profile/{current_user.get_id()}')


@application.route(f'/contest/<int:contest_id>/<path:function>', methods=["POST", "GET"])
@login_required
def contest_const(contest_id, function):
    if not contest_verifi_id(contest_id):
        flash(f'Контеста {contest_id} не существует!', 'warning')
        return redirect('/list')
    if not login_contest(contest_id):
        flash('У Вас нет доступа!', 'warning')
        return redirect('/list')

    if function == 'problems':
        task_all = literal_eval(*dbase.get_task(contest_id))
        ans = {}
        try:
            ans = requests.post(f'{url_server}/api-v.1.0/get_task_all',
                                params={'ids': ','.join(map(str, [i[1] for i in task_all]))}, verify=False).json()
        except requests.ConnectionError as e:
            print('Нет соединения: ', e)
        _dict_ = {}
        for i in range(len(ans)):
            _dict_[task_all[i][0]] = {'id': task_all[i][1], 'text': ans[str(task_all[i][1])]}
        return render_template('contest/contest_task.html',
                               header='Statistics.Contest',
                               header_map={'Обратно': '/list',
                                           'Архив задач': '/archive',
                                           'Профиль': f'/profile/{current_user.get_id()}'},
                               option_map={'Задачи': f'/contest/{contest_id}/problems',
                                           'Отправить': f'/contest/{contest_id}/send',
                                           'Мои посылки': f'/contest/{contest_id}/status?my=true',
                                           'Статус': f'/contest/{contest_id}/status',
                                           'Общие результаты': f'/contest/{contest_id}/result'},
                               task_list=_dict_,
                               title="Statistics.Online")
    if function.split('/')[0] == 'problems':
        try:
            text = function.split('/')
            # print(text)
            task_all = literal_eval(*dbase.get_task(contest_id))
            ans = {}
            try:
                ans = requests.post(f'{url_server}/api-v.1.0/get_task_all',
                                    params={'ids': ','.join(map(str, [i[1] for i in task_all]))}, verify=False).json()
            except requests.ConnectionError as e:
                print('Нет соединения: ', e)
            _dict_ = {}
            for i in range(len(ans)):
                _dict_[task_all[i][0]] = {'id': task_all[i][1], 'text': ans[str(task_all[i][1])]}
            type_problem = _dict_[text[-1]]['id']
            try:
                ans = requests.post(f'{url_server}/api-v.1.0/get_task', params={'id': type_problem},
                                    verify=False).json()
                # ans = requests.post('http://server.statistics-online.ru/api-v.1.0/get_task', params={'id':
                # type_problem}).json()
            except requests.ConnectionError as e:
                print('Нет соединения: ', e)
                return abort(502)
            # print(ans)
            ans['time_limit'] = int(ans['time_limit']) // 1000
            ans['task_text'] = ans['task_text'].replace('\n', '<br>')
            ans['score'] = ans['score'].replace('\n', '<br>')
            ans['task_input'] = ans['task_input'].replace('\n', '<br>')
            ans['task_output'] = ans['task_output'].replace('\n', '<br>')
            return render_template('contest/task.html',
                                   header='Statistics.Contest',
                                   header_map={'Обратно': '/list',
                                               'Архив задач': '/archive',
                                               'Профиль': f'/profile/{current_user.get_id()}'},
                                   option_map={'Задачи': f'/contest/{contest_id}/problems',
                                               'Отправить': f'/contest/{contest_id}/send',
                                               'Мои посылки': f'/contest/{contest_id}/status?my=true',
                                               'Статус': f'/contest/{contest_id}/status',
                                               'Общие результаты': f'/contest/{contest_id}/result'},
                                   task=ans,
                                   task_id=text[-1],
                                   title="Statistics.Online")
        except Exception:
            return redirect(f'/contest/{contest_id}/problems')
    if function == 'send':
        get_task = request.args.get('task')
        if not get_task:
            get_task = 'A'
        task_all = literal_eval(*dbase.get_task(contest_id))
        ans = {}
        try:
            ans = requests.post(f'{url_server}/api-v.1.0/get_task_all',
                                params={'ids': ','.join(map(str, [i[1] for i in task_all]))}, verify=False).json()
        except requests.ConnectionError as e:
            print('Нет соединения: ', e)
        _dict_ = {}
        for i in range(len(ans)):
            _dict_[task_all[i][0]] = {'id': task_all[i][1], 'text': ans[str(task_all[i][1])]}
        return render_template('contest/send_code.html',
                               header='Statistics.Contest',
                               header_map={'Обратно': '/list',
                                           'Архив задач': '/archive',
                                           'Профиль': f'/profile/{current_user.get_id()}'},
                               option_map={'Задачи': f'/contest/{contest_id}/problems',
                                           'Отправить': f'/contest/{contest_id}/send',
                                           'Мои посылки': f'/contest/{contest_id}/status?my=true',
                                           'Статус': f'/contest/{contest_id}/status',
                                           'Общие результаты': f'/contest/{contest_id}/result'},
                               get_task=get_task,
                               task=_dict_,
                               c_id=contest_id,
                               compiler=compiler,
                               title="Statistics.Online")
    if function == 'code_post':
        select_task, select_lang, select_code = request.form.get('comp_select'), request.form.get(
            'select'), request.form.get('code')
        ans = requests.post(f'{url_server}/api-v.1.0/code', json={'_id': select_task, 'lang': select_lang,
                                                                  'contest_id': contest_id,
                                                                  'user_id': current_user.get_id(),
                                                                  'code': json.loads(json.dumps(select_code,
                                                                                                ensure_ascii=False))},
                            verify=False)
        flash('Решение успешно отправлено!', category='success')
        return redirect(f'/contest/{contest_id}/status?my=true')
    if function == 'status':
        task_all = literal_eval(*dbase.get_task(contest_id))
        contest_config = dbase.get_format_of_contest(contest_id)[0]
        task_ = [i[1] for i in task_all]
        _dict_ans_ = {}
        if request.args.get('my') == 'true':
            ans = requests.post(f'{url_server}/api-v.1.0/testing_info', params={'my': 'true'},
                                json={'user_id': current_user.get_id(),
                                      'tasks': task_,
                                      'contest': contest_id}).json()
            for i in ans[-1::-1]:
                s = ''
                for j in task_all:
                    if j[1] == i[2][0]:
                        s = j[0]
                        break
                _dict_ans_[i[0]] = {
                    'time_post': datetime.strptime(i[1], '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d %H:%M:%S'),
                    'task_id': [i[2], s],
                    'user': [i[3], dbase.getLogin(i[3])[0]],
                    'contest': i[4],
                    'protocol': i[5],
                    'lang': i[6],
                    'status': i[7],
                    'test': i[12],
                    'fail': i[8],
                    'bad_time': i[9],
                    'bad_memory': i[10],
                    'points': i[11]
                }
            return render_template('contest/status_my.html',
                                   header='Statistics.Contest',
                                   header_map={'Обратно': '/list',
                                               'Архив задач': '/archive',
                                               'Профиль': f'/profile/{current_user.get_id()}'},
                                   option_map={'Задачи': f'/contest/{contest_id}/problems',
                                               'Отправить': f'/contest/{contest_id}/send',
                                               'Мои посылки': f'/contest/{contest_id}/status?my=true',
                                               'Статус': f'/contest/{contest_id}/status',
                                               'Общие результаты': f'/contest/{contest_id}/result'},
                                   title="Statistics.Online",
                                   result=_dict_ans_,
                                   contest_config=contest_config)
        ans = requests.post(f'{url_server}/api-v.1.0/testing_info', json={
            'tasks': task_,
            'contest': contest_id}, verify=False).json()
        for i in ans[-1::-1]:
            s = ''
            for j in task_all:
                if j[1] == i[2][0]:
                    s = j[0]
                    break
            _dict_ans_[i[0]] = {
                'time_post': datetime.strptime(i[1], '%Y-%m-%d %H:%M:%S.%f').strftime('%Y-%m-%d %H:%M:%S'),
                'task_id': [i[2], s],
                'user': [i[3], dbase.getLogin(i[3])[0]],
                'contest': i[4],
                'protocol': i[5],
                'lang': i[6],
                'status': i[7],
                'test': i[12],
                'fail': i[8],
                'bad_time': i[9],
                'bad_memory': i[10],
                'points': i[11]
            }
        return render_template('contest/status.html',
                               header='Statistics.Contest',
                               header_map={'Обратно': '/list',
                                           'Архив задач': '/archive',
                                           'Профиль': f'/profile/{current_user.get_id()}'},
                               option_map={'Задачи': f'/contest/{contest_id}/problems',
                                           'Отправить': f'/contest/{contest_id}/send',
                                           'Мои посылки': f'/contest/{contest_id}/status?my=true',
                                           'Статус': f'/contest/{contest_id}/status',
                                           'Общие результаты': f'/contest/{contest_id}/result'},
                               title="Statistics.Online",
                               result=_dict_ans_,
                               contest_config=contest_config)
    return abort(404)


@application.route('/test_file')
def example_ok():
    return '<form action="/api-v.1.0/task_code" enctype="multipart/form-data" method="POST">' \
           '    <input type="file" name="file">' \
           '    <input type="radio" value="python3" id="1" name="comp">' \
           '    <label for="1">Python 3.9</label>' \
           '    <input type="radio" value="python2" id="2" name="comp">' \
           '    <label for="2">Python 2.7</label>' \
           '    <input type="radio" value="pypy3" id="3" name="comp">' \
           '    <label for="3">PyPy 3.9</label>' \
           '    <input type="radio" value="pypy2" id="4" name="comp">' \
           '    <label for="4">PyPy 2.7</label>' \
           '    <input type="submit">' \
           '</form>'


@application.route("/api-v.1.0/testing", methods=['GET', 'POST'], subdomain='practice')
def proxy_example():
    print(1)


"""===============ABORT()==============="""


@application.errorhandler(400)
def page_not_found(e):
    return render_template('errors_pages/error_base.html',
                           number_error='400',
                           number_error_len=3,
                           text_problem='Bad Request',
                           title="Statistics.Error",
                           _list_={'На главную': '/'}), 400


@application.errorhandler(404)
def page_not_found(e):
    return render_template('errors_pages/error_base.html',
                           number_error='404',
                           number_error_len=3,
                           text_problem='Not Found («не найдено»)',
                           title="Statistics.Error",
                           _list_={'На главную': '/'}), 404


@application.errorhandler(500)
def page_not_found(e):
    return render_template('errors_pages/error_base.html',
                           number_error='500',
                           number_error_len=3,
                           text_problem='Internal Server Error («внутренняя ошибка сервера»)',
                           _list_={'На главную': '/'},
                           title="Statistics.Error"), 500


@application.route('/testing')
def testing():
    d = requests.post('http://192.168.1.70:5001/api-v.1.0/get_task?id=1').json()
    return json.dumps(d,
                      sort_keys=False,
                      indent=4,
                      ensure_ascii=False,
                      separators=(',', ': '))


if __name__ == '__main__':
    application.run(host='localhost', port=5000, debug=False, threaded=True)
