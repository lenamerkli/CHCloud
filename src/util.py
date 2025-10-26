from dotenv import load_dotenv
from logging import getLogger as GetLogger, Formatter as LogFormatter, FileHandler as LogFileHandler
from logging import INFO as LOG_INFO  # noqa
from os import environ


__all__ = [
    'DATE_FORMAT',
    'DEVELOPMENT',
    'setup_logger',
]


load_dotenv()
DATE_FORMAT = '%Y-%m-%d_%H-%M-%S'
DEVELOPMENT = environ.get('ENVIRONMENT', '') == 'dev'


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
