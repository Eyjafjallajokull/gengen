import logging
from unittest import TestCase
from genetics.accuracy import AccuracyMachine
from lib.config import readConfig
import lib.log as log

class TestGenome(TestCase):
    def setUp(self):
        self.cfg = readConfig('tests/fixtures/config/basic.yml')
        log.log = logging.getLogger('population')
        log.log.addHandler(logging.NullHandler())
        self.object = AccuracyMachine()

    def tearDown(self):
        self.object.remove()
    #todo: implement tests