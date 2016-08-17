import logging
import sys
import lib.config as config

INFO = logging.INFO
DEBUG = logging.DEBUG
ERROR = logging.ERROR
log = None


def init_logger():
    global log
    raw_formatter = logging.Formatter('%(asctime)s;%(caller)s;%(levelname)s;%(message)s')
    pretty_formatter = logging.Formatter('%(message)s')
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(pretty_formatter)
    file_handler = logging.FileHandler(config.config['main']['logPath'])
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(raw_formatter)
    log = logging.getLogger('population')
    if config.config['debug']:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    log.addHandler(stdout_handler)
    log.addHandler(file_handler)
    return log


def info(msg, *args, **kwargs):
    kwargs['extra'] = {'caller': sys._getframe(1).f_globals['__name__']}
    log.info(msg, *args, **kwargs)


def debug(msg, *args, **kwargs):
    kwargs['extra'] = {'caller': sys._getframe(1).f_globals['__name__']}
    log.debug(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    kwargs['extra'] = {'caller': sys._getframe(1).f_globals['__name__']}
    log.error(msg, *args, **kwargs)


def add_message(level, msg, *args, **kwargs):
    kwargs['extra'] = {'caller': sys._getframe(1).f_globals['__name__']}
    log.log(level, msg, *args, **kwargs)
