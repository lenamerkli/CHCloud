from datetime import datetime
from os import urandom
from base64 import urlsafe_b64encode

from database import *


__all__ = [
    'rand_base16',
    'rand_base64',
    'rand_salt',
]


def rand_base64(digits: int) -> str:
    """
    Generates a new string of random base64 characters
    :param digits: the length of the string to be generated
    :return: a random string of base64 characters
    """
    while True:
        n = urlsafe_b64encode(urandom(digits)).decode()[:digits]
        result = query_db('SELECT * FROM used_ids WHERE id=?', (n,), True)
        if not result:
            query_db('INSERT INTO used_ids VALUES (?, ?)', (n, datetime.now().strftime(DATE_FORMAT)))
            return n


def rand_base16(digits: int) -> str:
    """
    Generates a new string of random base16 characters
    :param digits: the length of the string to be generated
    :return: a random string of base16 characters
    """
    while True:
        n = urandom(digits).hex()[:digits]
        result = query_db('SELECT * FROM used_ids WHERE id=?', (n,), True)
        if not result:
            query_db('INSERT INTO used_ids VALUES (?, ?)', (n, datetime.now().strftime(DATE_FORMAT)))
            return n


def rand_salt() -> str:
    """
    Generates a random salt
    :return: a random salt
    """
    return urlsafe_b64encode(urandom(32)).decode()
