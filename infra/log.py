import os

import logging
from logging.handlers import RotatingFileHandler


def init_logger(name, level=logging.DEBUG):
    log_path = f'logs/{name}.log'
    os.makedirs(os.path.split(log_path)[0], exist_ok=True)
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                        level=level)
    log_handler = RotatingFileHandler(log_path, maxBytes=100 * 1024 * 1024, backupCount=5)
    log_handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)-12s [%(levelname)s] %(message)s')
    log_handler.setFormatter(formatter)
    logging.getLogger('').addHandler(log_handler)

    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def debug(msg):
    logging.debug(msg)
    print(msg)
