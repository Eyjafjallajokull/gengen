from unittest import TestCase
from lib.common import randNumber

class TestRandNumber(TestCase):
    def test_randNumber(self):
        arguments = (
            (10, 20, 1),
            (10, 13, 7),
            (-10, 20, 1)
        )
        for base, limit, distance in arguments:
            r = [ randNumber(base, limit, distance) for x in xrange(0, 10000) ]
            maxv = max(r)
            minv = min(r)
            self.assertLessEqual(maxv, base+distance/2.0)
            self.assertGreaterEqual(minv, base-distance/2.0)
