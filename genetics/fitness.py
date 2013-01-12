from lib import image

class BaseFitnessMachine(object):
    def __init__(self, target):
        self.target = target

    def calculate(self, genome):
        pass

class MeshFitnessMachine(BaseFitnessMachine):
    def __init__(self, target, renderer):
        self.target = target
        self.renderer = renderer

    def calculate(self, genome):
        self.renderer.renderToFile(genome)
        return image.compare(self.target, genome.pngPath)

class TestFitnessMachine(BaseFitnessMachine):
    def calculate(self, genome):
        diff = 0
        for i in xrange(0, len(self.target)):
            if self.target[i] != genome.data[i]:
                diff += 1
        return diff
