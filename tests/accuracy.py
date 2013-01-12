import logging
from unittest import TestCase
from genetics.accuracy import AccuracyMachine
from lib.config import readConfig

class TestGenome(TestCase):
    def setUp(self):
        self.cfg = readConfig('tests/fixtures/config/basic.yml')
        logger = logging.getLogger('population')
        logger.addHandler(logging.NullHandler())
        self.object = AccuracyMachine(logger)

    def tearDown(self):
        self.object.remove()
    #todo: implement tests