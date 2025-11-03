from base64 import urlsafe_b64decode
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import request, session, Blueprint
from hashlib import pbkdf2_hmac
from logging import log
from os import environ
from pydantic import BaseModel, ValidationError
from pyotp import TOTP
from secrets import randbelow
from time import sleep
from user_agents import parse

from database import *
from rand import *
from user_class import *
from util import *


__all__ = [
    'hash_password',
    'parse_login_user_agent',
    'get_user_id',
    'create_session',
    'invalidate_session',
    'login_blueprint',
]


class RLoginData(BaseModel):
    email: str
    password: str
    totp: str


load_dotenv()


def hash_password(password: str, salt: bytes):
    return pbkdf2_hmac(
        hash_name='sha3_512',
        password=urlsafe_b64decode(environ['HASH_PEPPER_1']) + password.encode() + urlsafe_b64decode(environ['HASH_PEPPER_2']),
        salt=salt,
        iterations=int(environ['HASH_ITERATIONS']),
    )


def parse_login_user_agent() -> str:
    ua = parse(request.headers.get('User-Agent', ''))
    os_name = ua.os.family or 'Unknown'
    browser_name = ua.browser.family or 'Unknown'
    return f"{os_name.replace(' ', '')}-{browser_name.replace(' ', '')}"


def get_user_id(no_invalidation=False):
    if 'token' in session:
        db_result = query_db('SELECT id, user_id, created, expires, browser FROM sessions WHERE id=?', (session['token'],), True)
        if db_result:
            if db_result[3] < datetime.now().strftime(DATE_FORMAT):
                if db_result[4] == parse_login_user_agent():
                    if query_db('SELECT id FROM users WHERE id=?', (db_result[1],), True):
                        return db_result[1]
                    elif not no_invalidation:
                        invalidate_session()
                elif not no_invalidation:
                    invalidate_session()
    return None


def create_session(user_id: str):
    session['token'] = rand_base64(64)
    query_db('INSERT INTO sessions (id, user_id, created, expires, browser) VALUES (?, ?, ?, ?, ?)', (session['token'], user_id, datetime.now().strftime(DATE_FORMAT), (datetime.now() + timedelta(days=32)).strftime(DATE_FORMAT), parse_login_user_agent()))


def invalidate_session():
    if 'token' in session:
        query_db('UPDATE sessions SET expires=? WHERE id=?', (datetime.now().strftime(DATE_FORMAT), session['token']))
    session['token'] = ''


login_blueprint = Blueprint('login', __name__)


@login_blueprint.route('/api/v1/login', methods=['POST'])
def r_login():
    try:
        data = dict(request.get_json(silent=True))
    except Exception as e:
        log(20, e)
        return {'error': 'Invalid JSON'}, 400
    try:
        login_data = dict(RLoginData(**data))
    except ValidationError as e:
        log(20, e.errors())
        return {'error': 'Invalid data'}, 400
    user_id: list = query_db('SELECT id FROM users WHERE email=?', (login_data['email'],), True)
    authentication_error = {'error': 'authentication error', 'message': 'Invalid email, password, or TOTP'}, 400
    sleep((randbelow(2 ** 16) / (2 ** 16)) / 7)
    if not user_id:
        return authentication_error
    user_id: str = user_id[0]
    user = User.load(user_id)
    if user.password != hash_password(login_data['password'], user.salt):
        return authentication_error
    totp = TOTP(user.totp)
    if not totp.verify(login_data['totp'], valid_window=1):
        return authentication_error
    create_session(user_id)
    user.last_login = datetime.now()
    user.save()
    return {'success': 'success', 'message': 'Successfully signed-in.'}, 200


@login_blueprint.route('/api/v1//logout', methods=['GET', 'POST'])
def r_logout():
    invalidate_session()
    return {'success': 'success', 'message': 'Successfully signed-out.'}, 200
