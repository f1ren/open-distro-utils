import sys

import os

import logging
from logging.handlers import RotatingFileHandler


def init_logger(name=None, level=logging.DEBUG):
    filename = get_log_file_name(name)
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                        level=level)
    file_handler = get_file_handler(filename, level)

    logging.getLogger('').addHandler(file_handler)
    logging.getLogger('requests_log').addHandler(
        get_file_handler(
            filename.replace('.log', '-requests.log'), level
        )
    )

    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    info(f'Logging to {filename}')


def get_file_handler(filename, level):
    file_handler = RotatingFileHandler(filename, maxBytes=100 * 1024 * 1024, backupCount=5)
    file_handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)-12s [%(levelname)s] %(message)s')
    file_handler.setFormatter(formatter)
    return file_handler


def get_log_file_name(name):
    import __main__
    main_file_path = __main__.__file__
    main_dir, main_file_name = os.path.split(main_file_path)

    if name is None:
        name = os.path.splitext(main_file_name)[0]

    parent_dir = os.path.split(main_dir)[0]
    if parent_dir == '':
        parent_dir = '..'
    log_dir = os.path.join(parent_dir, f'{name}-logs')
    os.makedirs(log_dir, exist_ok=True)
    filename = os.path.join(log_dir, f'{name}.log')
    return filename


def info(msg):
    logging.info(msg)


def debug(msg):
    logging.debug(msg)


log_request = logging.getLogger('requests_log').debug
