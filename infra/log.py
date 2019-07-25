import os

import logging
from logging.handlers import RotatingFileHandler


def init_logger(name=None, level=logging.DEBUG):
    filename = get_log_file_name(name)
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                        level=level)
    log_handler = RotatingFileHandler(filename, maxBytes=100 * 1024 * 1024, backupCount=5)
    log_handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)-12s [%(levelname)s] %(message)s')
    log_handler.setFormatter(formatter)
    logging.getLogger('').addHandler(log_handler)

    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_log_file_name(name):
    import __main__
    main_file_path = __main__.__file__
    main_dir, main_file_name = os.path.split(main_file_path)

    if name is None:
        name = os.path.splitext(main_file_name)[0]

    log_dir = os.path.split(main_dir)[0] + f'/{name}-logs'
    os.makedirs(log_dir, exist_ok=True)
    filename = f'{log_dir}/{name}.log'
    return filename


def debug(msg):
    logging.debug(msg)
