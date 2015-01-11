from lib import image
from time import time
import lib.log as log


class BaseFitnessMachine(object):
    def __init__(self, target):
        self.target = target

    def calculate(self, genome):
        pass


class MeshFitnessMachine(BaseFitnessMachine):
    def __init__(self, target, renderer):
        super(MeshFitnessMachine, self).__init__(target)
        self.renderer = renderer

    def calculate(self, genome):
        start = time()
        self.renderer.renderToFile(genome)
        log.debug('render time %f' % (time()-start))
        fitness = image.compare(self.target, genome.pngPath)
        log.debug('calculated fitness for %s: %s' % (genome.serial, fitness))
        return fitness


class TestFitnessMachine(BaseFitnessMachine):
    def calculate(self, genome):
        diff = 0
        for i in xrange(0, len(self.target)):
            if self.target[i] != genome.data[i]:
                diff += 1
        return diff
