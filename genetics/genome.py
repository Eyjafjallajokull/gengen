import math
from genetics.fitness import *
from lib.common import *
import pickle
import random
import copy
import lib.config as config
import lib.log as log

class Genome(object):
    fitnessMachine = BaseFitnessMachine
    def __init__(self, serial=None):
        if not serial:
            serial = str(int(random.random()*10000000))
        self.serial = serial
        self.data = None
        self.objPath = config.config['main']['populationRamPath']+self.serial+'_genome.obj'
        self.logPath = config.config['main']['populationRamPath']+self.serial+'.log'
        self.fitness = 999999999
        self.dataModified = False
        self.generation = 0

    def __str__(self):
        return self.__class__.__name__ + self.serial

    def __repr__(self):
        return self.__class__.__name__ + self.serial

    def save(self):
        pickle.dump(self, open(self.objPath, 'wb'))

    def remove(self):
        do('rm -f %s' % config.config['main']['populationRamPath']+self.serial+'*')

    def create(self):
        self._create()
        self.dataModified = True

    def createWithCrossover(self, genomeA, genomeB):
        if not isinstance(genomeA, Genome) or not isinstance(genomeB, Genome):
            raise ValueError('genomes must be instance of Genome')
        self._createWithCrossover(genomeA, genomeB)
        self.dataModified = True

    def _createWithCrossover(self, genomeA, genomeB):
        self.data = copy.deepcopy(genomeA.data)
        genomeSize = len(genomeA.data) if len(genomeA.data) < len(genomeB.data) else len(genomeB.data)
        crossoverObjectCount = int(math.ceil(genomeSize * config.config['ga']['crossoverObjectCountMultiplier']))
        log.debug('%s crossover: objects=%d' % (self.serial, crossoverObjectCount))
        if crossoverObjectCount < genomeSize:
            for i in random.sample(xrange(0, genomeSize), crossoverObjectCount):
                self.data[i] = copy.deepcopy(genomeB.data[i])

    def mutate(self):
        self._mutate()
        self.dataModified = True

    def setFitness(self, fitness):
        self.fitness = fitness
        self.dataModified = False

    def _mutate(self): pass
    def _create(self): pass

class MeshGenome(Genome):
    fitnessMachine = MeshFitnessMachine
    meshConstraints = (7+3, 5+3, 3)
    def __init__(self, serial=None):
        super(MeshGenome, self).__init__(serial)
        self.blendPath = config.config['main']['populationRamPath']+self.serial+'.blend'
        self.dataPath = config.config['main']['populationRamPath']+self.serial+'_data.obj'
        self.pngPath = config.config['main']['populationRamPath']+self.serial+'.png'

    def _create(self):
        self.data = []
        for i in range(0, config.config['ga']['genomeSize']):
            self.data.append(self._createObject())

    def _createObject(self):
        obj = []
        for _ in [0,1,2]:
            obj.append([rand(self.meshConstraints[0]), rand(self.meshConstraints[1]), rand(self.meshConstraints[2])])
        self._sortObjectPoints(obj)
        return obj

    def _createWithCrossover(self, genomeA, genomeB):
        super(MeshGenome, self)._createWithCrossover(genomeA, genomeB)
        if config.config['ga']['genomeSize'] - len(self.data) > 0:
            for _ in range(0, config.config['ga']['genomeSize']-len(self.data)):
                self.data.append(self._createObject())


    def _sortObjectPoints(self, object):
        """ sort object points clockwise """
        object.sort(lambda a, b: cmp(a[0], b[0]))
        left = object.pop(0)
        object.sort(lambda a, b: -cmp(a[1], b[1]))
        top = object.pop(0)
        object.insert(0, top)
        object.insert(0, left)

    def _mutate(self):
        objectCount = int(math.ceil(config.config['ga']['mutationObjectCountMultiplier'] * config.config['ga']['genomeSize']))
        pointCount = config.config['ga']['mutationPointCount']
        coordinateCount = config.config['ga']['mutationCoordinateCount']
        randomizeMultiplier = config.config['ga']['mutationRandomizeMultiplier']
        log.debug('%s mutation: objects=%d points=%d coords=%d rand=%f' %
                  (self.serial, objectCount, pointCount, coordinateCount, randomizeMultiplier))
        for object in random.sample(xrange(0,len(self.data)), objectCount):
            pointsToMutate = random.sample([0,1,2], pointCount)
            for point in pointsToMutate:
                coordinatesToMutate = random.sample([0,1,2], coordinateCount)
                for coordinate in coordinatesToMutate:
                    self.data[object][point][coordinate] = randNumber(self.data[object][point][coordinate],
                        self.meshConstraints[coordinate], randomizeMultiplier)
            self._sortObjectPoints(self.data[object])

class TestGenome(Genome):
    fitnessMachine = TestFitnessMachine
    def _create(self):
        self.data = [ int(random.randrange(0,2)) for i in range(0, config.config['ga']['genomeSize'])]

    def _mutate(self):
        for i in random.sample(xrange(0, len(self.data)), config.config['ga']['mutationObjectCountMultiplier']):
            self.data[i] = int(randNumber(self.data[i], 2, config.config['ga']['mutationRandomizeMultiplier']))
        self.save()


class MetaGenome(Genome):
    base = {
        'ga': {
            'populationSize': (1,20,50),
            'genomeSize': (1,5,10),
            'mutationRandomizeMultiplier': (0.1, 0.5, 1, 2),
            'generations': (400,),
            'selectionMultiplier': (0.25, 0.5),
            'crossoverObjectCountMultiplier': (0.1, 0.25, 0.5),
            'crossoverAllNew': (1,),
            'mutationObjectCountMultiplier': (0.25, 0.5, 0.75)
        },
        'main': {
            'populationPath': '/media/dane/dokumenty/Galeria/3d/gen-gen/build/simple1_population/',
            'baseBlendPath': '/media/dane/dokumenty/Galeria/3d/gen-gen/main.blend',
            'baseImage': '/media/dane/dokumenty/Galeria/3d/gen-gen/build/simple1.png'
        }
    }
    cfg = {
        'ga': {'mutationFactor': 1}
    }
    def __init__(self):
        super(MetaGenome, self).__init__()

    def create(self):
        self.data = copy.deepcopy(self.base)
        for (sectionName, section) in self.data.items():
            for (paramName, param) in section.items():
                self.data[sectionName][paramName] = random.choice(param)

    def createWithCrossover(self, genomeA, genomeB):
        self.data = copy.deepcopy(genomeA.data)
        for i in range(0, len(self.data)):
            param = random.choice(self.base['ga'].keys())
            pass

    def mutate(self):
        for i in range(0, config.config['ga']['mutationFactor']):
            param = random.choice(self.base['ga'].keys())
            value = None
            while True:
                value = random.choice(self.base['ga'][param])
                if self.data['ga'][param] != value:
                    break
            self.data['ga'][param] = value

    def calculateFitness(self):
        pop = Population(self.data)
        pop.evolve()
        return pop.getBestGenome().fitness
