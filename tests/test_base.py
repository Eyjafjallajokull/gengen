import logging
from unittest import TestCase
from lib.config import readConfig
import lib.log as log

class TestBase(TestCase):
    def initConfig(self, name):
        self.cfg = readConfig('tests/fixtures/config/%s.yml' % name)

    def initLog(self):
        log.log = logging.getLogger('population')
        log.log.addHandler(logging.NullHandler())