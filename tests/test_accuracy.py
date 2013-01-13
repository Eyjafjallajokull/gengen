import math
from tests.test_base import TestBase
from genetics.accuracy import AccuracyMachine, AccuracyParam

class TestAccuracyMachine(TestBase):
    def setUp(self):
        self.initConfig('basic')
        self.initLog()
        self.object = AccuracyMachine()

class TestAccuracyParam(TestBase):
    data = {
        'float': {
            'multiplier': 0.5,
            'minimum': 0.1,
            'int': 0,
            'start': 3
        },
        'int': {
            'multiplier': 0.5,
            'minimum': 0.1,
            'int': 1,
            'start': 3
        }
    }

    def setUp(self):
        self.initLog()

    def test_getNextValue(self):
        for (name, cfg) in self.data.items():
            object = AccuracyParam(name, cfg, cfg['start'])
            (real, scaled) = object.getNextValue()
            if cfg['int'] == 1:
                self.assertEqual(real, int(math.ceil(cfg['start']*cfg['multiplier'])))
            else:
                self.assertEqual(real, cfg['start']*cfg['multiplier'])
            self.assertEqual(scaled, cfg['start']*cfg['multiplier'])

    def test_limit(self):
        cfg = self.data['float']
        object = AccuracyParam('float', cfg, cfg['start'])
        for _ in range(0,100):
            object.increase()
        self.assertGreaterEqual(object.currentValue, cfg['minimum'])
        self.assertFalse(object.canIncrease())
