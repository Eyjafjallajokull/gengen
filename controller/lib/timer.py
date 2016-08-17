from time import time
import lib.log as log


class Timer(object):
    def __init__(self, message, level=log.DEBUG):
        self.message = message
        self.level = level
        self.started = None

    def __enter__(self):
        self.started = time()

    def __exit__(self, type, value, traceback):
        duration = time() - self.started
        log.add_message(self.level, self.message % duration)
