from lib.timer import Timer
import lib.log as log


class BaseFitnessMachine(object):
    def __init__(self, target):
        self.target = target

    def calculate(self, genome):
        pass


class MeshFitnessMachine(BaseFitnessMachine):
    def __init__(self, target, renderer, qualifier):
        super(MeshFitnessMachine, self).__init__(target)
        self.renderer = renderer
        self.qualifier = qualifier

    def calculate(self, genome):
        with Timer('render time %f'):
            self.renderer.render_to_file(genome)

        with Timer('qualify time %f'):
            fitness = self.qualifier.calculate(self.target, genome.pngPath)

        log.debug('calculated fitness for %s: %s' % (genome.serial, fitness))
        return fitness


class TestFitnessMachine(BaseFitnessMachine):
    def calculate(self, genome):
        diff = 0
        for i in xrange(0, len(self.target)):
            if self.target[i] != genome.data[i]:
                diff += 1
        return diff
