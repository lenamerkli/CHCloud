from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask, g, request, Response, send_from_directory
from logging import getLogger as GetLogger, Formatter as LogFormatter, FileHandler as LogFileHandler, basicConfig as log_basicConfig
from logging import INFO as LOG_INFO  # noqa
from os import environ, urandom
from os.path import exists, join
from requests import request as requests_send
from sqlite3 import connect as sqlite_connect, Connection as SQLite_Connection

DATE_FORMAT = '%Y-%m-%d_%H-%M-%S'

load_dotenv()

DEVELOPMENT = environ.get('ENVIRONMENT', '') == 'dev'
app = Flask(__name__)

if not exists(join(app.root_path, 'resources', 'key.bin')):
    with open(join(app.root_path, 'resources', 'key.bin'), 'wb') as _f:
        _f.write(urandom(64))
with open(join(app.root_path, 'resources', 'key.bin'), 'rb') as _f:
    _secret_key = _f.read()
app.secret_key = _secret_key


if DEVELOPMENT:
    app.config.update(
        SESSION_COOKIE_NAME='session',
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=False,
        SESSION_COOKIE_SAMESITE='Strict',
        PERMANENT_SESSION_LIFETIME=timedelta(days=128),
    )
else:
    app.config.update(
        SESSION_COOKIE_NAME='__Host-session',
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_SAMESITE='Strict',
        PERMANENT_SESSION_LIFETIME=timedelta(days=128),
    )


def setup_logger(name, file):
    """
    Creates a new logging instance
    :param name: the name
    :param file: path to the file to which the contents will be written
    :return:
    """
    logger = GetLogger(name)
    formatter = LogFormatter('%(asctime)s\t%(message)s', datefmt='%Y-%m-%d_%H-%M-%S')
    file_handler = LogFileHandler(file, mode='a')
    file_handler.setFormatter(formatter)
    logger.setLevel(LOG_INFO)
    logger.addHandler(file_handler)
    logger.propagate = False


log_basicConfig(filename='main.log', format='%(asctime)s\t%(message)s', datefmt=DATE_FORMAT, level=LOG_INFO)

setup_logger('access', join(app.root_path, 'logs', 'access.log'))
access_log = GetLogger('access')


def get_db() -> SQLite_Connection:
    """
    Gets the database instance
    :return: a pointer to the database
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite_connect('database.sqlite')
    return db


@app.teardown_appcontext
def close_connection(exception=None) -> None:  # noqa
    """
    destroys the database point
    :param exception: unused
    :return:
    """
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False) -> list | tuple:
    """
    Runs a SQL query
    :param query: the query as a SQL statement
    :param args: arguments to be inserted into the query
    :param one: if this function should only return one result
    :return: the data from the database
    """
    conn = get_db()
    cur = conn.execute(query, args)
    result = cur.fetchall()
    conn.commit()
    cur.close()
    return (result[0] if result else None) if one else result


with app.app_context():
    with open(join(app.root_path, 'resources/create_database.sql'), 'r') as f:
        _create_db = f.read()
    _conn = get_db()
    _conn.executescript(_create_db)
    _conn.commit()
    _conn.close()


@app.errorhandler(404)
def error_handler_404(*_, **__):
    if DEVELOPMENT:
        res = requests_send(
            method=request.method,
            url='http://' + request.url.replace(request.host_url, 'localhost:4200/'),  # noqa
            headers={k: v for k, v in request.headers if k.lower() != 'host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=True,
        )
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [
            (k, v) for k, v in res.raw.headers.items()
            if k.lower() not in excluded_headers
        ]
        response = Response(res.content, res.status_code, headers)  # noqa
        return response
    else:
        path = request.path
        if path and path.startswith('/'):
            path = path[1:]
        if path != '' and exists(join(app.root_path, 'web', path)):
            return send_from_directory(join(app.root_path, 'web'), path), 200
        else:
            return send_from_directory(join(app.root_path, 'web'), 'index.html'), 200


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=False)
