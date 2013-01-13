import logging
import sys
log = None
import lib.config as config

def initLogger():
    global log
    rawFormatter = logging.Formatter('%(asctime)s;%(caller)s;%(levelname)s %(message)s')
    prettyFormatter = logging.Formatter('%(message)s')
    stdoutHandler = logging.StreamHandler(sys.stdout)
    stdoutHandler.setLevel(logging.INFO)
    stdoutHandler.setFormatter(prettyFormatter)
    fileHandler = logging.FileHandler(config.config['main']['logPath'])
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(rawFormatter)
    log = logging.getLogger('population')
    log.setLevel(logging.DEBUG)
    log.addHandler(stdoutHandler)
    log.addHandler(fileHandler)
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