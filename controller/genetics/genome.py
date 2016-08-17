import math
from genetics.fitness import *
from lib.common import *
import pickle
import random
import copy
import glob
import os
import lib.config as config
import lib.log as log
import numpy as np


class Genome(object):
    fitnessMachine = BaseFitnessMachine

    def __init__(self, serial=None):
        if not serial:
            serial = str(int(random.random()*100000000000))
        self.serial = serial
        self.data = None
        self.objPath = config.config['main']['populationPath']+self.serial+'_genome.obj'
        self.logPath = config.config['main']['populationPath']+self.serial+'.log'
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
        file_list = glob.glob(config.config['main']['populationPath']+self.serial+'*')
        for f in file_list:
            os.remove(f)
        # do('timeout 3s rm -f %s' % (config.config['main']['populationRamPath']+self.serial+'*'))

    def create(self):
        self._create()
        self.dataModified = True

    def create_with_crossover(self, genome_a, genome_b):
        if not isinstance(genome_a, Genome) or not isinstance(genome_b, Genome):
            raise ValueError('genomes must be instance of Genome')
        self._create_with_crossover(genome_a, genome_b)
        self.dataModified = True

    def _create_with_crossover(self, genome_a, genome_b):
        self.data = copy.deepcopy(genome_a.data)
        genome_size = len(genome_a.data) if len(genome_a.data) < len(genome_b.data) else len(genome_b.data)
        crossover_object_count = int(math.ceil(genome_size * config.config['ga']['crossoverObjectCountMultiplier']))
        log.debug('%s crossover: objects=%d' % (self.serial, crossover_object_count))
        if crossover_object_count < genome_size:
            for i in random.sample(xrange(0, genome_size), crossover_object_count):
                self.data[i] = copy.deepcopy(genome_b.data[i])

    def mutate(self):
        self._mutate()
        self.dataModified = True

    def set_fitness(self, fitness):
        self.fitness = fitness
        self.dataModified = False

    def _mutate(self):
        pass

    def _create(self):
        pass


class MeshGenome(Genome):
    fitnessMachine = MeshFitnessMachine
    meshConstraints = (7, 5, 1)

    def __init__(self, serial=None):
        super(MeshGenome, self).__init__(serial)
        self.blendPath = config.config['main']['populationPath']+self.serial+'.blend'
        self.dataPath = config.config['main']['populationPath']+self.serial+'_data.obj'
        self.pngPath = config.config['main']['populationPath']+self.serial+'.png'

    def _create(self):
        self.data = []
        for i in range(0, config.config['ga']['genomeSize']):
            self.data.append(self._create_object())

    def _create_object(self):
        obj = [[rand(self.meshConstraints[0]), rand(self.meshConstraints[1]), rand(self.meshConstraints[2])]]
        while True:
            for _ in [1, 2]:
                i = rand(1)
                obj.append([obj[0][0]+rand(i), obj[0][1]+rand(i), obj[0][2]+rand(i)])
            if self._validate_size(obj):
                break
        self._sort_object_points(obj)
        return obj

    def _create_with_crossover(self, genome_a, genome_b):
        super(MeshGenome, self)._create_with_crossover(genome_a, genome_b)
        missing_object_count = config.config['ga']['genomeSize'] - len(self.data)
        if missing_object_count > 0:
            for _ in range(0, missing_object_count):
                self.data.append(self._create_object())

    def _sort_object_points(self, obj):
        """ sort object points clockwise """
        obj.sort(lambda a, b: cmp(a[0], b[0]))
        left = obj.pop(0)
        obj.sort(lambda a, b: -cmp(a[1], b[1]))
        top = obj.pop(0)
        obj.insert(0, top)
        obj.insert(0, left)

    def _mutate(self):
        object_count = int(math.ceil(config.config['ga']['mutationObjectCountMultiplier'] * config.config['ga']['genomeSize']))
        point_count = config.config['ga']['mutationPointCount']
        coordinate_count = config.config['ga']['mutationCoordinateCount']
        randomize_multiplier = config.config['ga']['mutationRandomizeMultiplier']
        log.debug('%s mutation: objects=%d points=%d coords=%d rand=%f' %
                  (self.serial, object_count, point_count, coordinate_count, randomize_multiplier))
        for obj in random.sample(xrange(0, len(self.data)), object_count):
            points_to_mutate = random.sample([0, 1, 2], point_count)
            coordinates_to_mutate = random.sample([0, 1, 2], coordinate_count)
            while True:
                for point in points_to_mutate:
                    for coordinate in coordinates_to_mutate:
                            self.data[obj][point][coordinate] = randNumber(self.data[obj][point][coordinate],
                                self.meshConstraints[coordinate]+2, randomize_multiplier)
                if self._validate_size(self.data[obj]):
                    break
            self._sort_object_points(self.data[obj])

    def _validate_size(self, obj):
        return triangle_area(obj) < config.config['main']['triangleSize']


class TestGenome(Genome):
    fitnessMachine = TestFitnessMachine

    def _create(self):
        self.data = [ int(random.randrange(0,2)) for i in range(0, config.config['ga']['genomeSize'])]

    def _mutate(self):
        for i in random.sample(xrange(0, len(self.data)), config.config['ga']['mutationObjectCountMultiplier']):
            self.data[i] = int(randNumber(self.data[i], 2, config.config['ga']['mutationRandomizeMultiplier']))
        self.save()


# class MetaGenome(Genome):
#     base = {
#         'ga': {
#             'populationSize': (1,20,50),
#             'genomeSize': (1,5,10),
#             'mutationRandomizeMultiplier': (0.1, 0.5, 1, 2),
#             'generations': (400,),
#             'selectionMultiplier': (0.25, 0.5),
#             'crossoverObjectCountMultiplier': (0.1, 0.25, 0.5),
#             'crossoverAllNew': (1,),
#             'mutationObjectCountMultiplier': (0.25, 0.5, 0.75)
#         },
#         'main': {
#             'populationPath': '/media/dane/dokumenty/Galeria/3d/gen-gen/build/simple1_population/',
#             'baseBlendPath': '/media/dane/dokumenty/Galeria/3d/gen-gen/main.blend',
#             'baseImage': '/media/dane/dokumenty/Galeria/3d/gen-gen/build/simple1.png'
#         }
#     }
#     cfg = {
#         'ga': {'mutationFactor': 1}
#     }
#
#     def __init__(self):
#         super(MetaGenome, self).__init__()
#
#     def create(self):
#         self.data = copy.deepcopy(self.base)
#         for (sectionName, section) in self.data.items():
#             for (paramName, param) in section.items():
#                 self.data[sectionName][paramName] = random.choice(param)
#
#     def create_with_crossover(self, genome_a, genome_b):
#         self.data = copy.deepcopy(genome_a.data)
#         for i in range(0, len(self.data)):
#             param = random.choice(self.base['ga'].keys())
#             pass
#
#     def mutate(self):
#         for i in range(0, config.config['ga']['mutationFactor']):
#             param = random.choice(self.base['ga'].keys())
#             value = None
#             while True:
#                 value = random.choice(self.base['ga'][param])
#                 if self.data['ga'][param] != value:
#                     break
#             self.data['ga'][param] = value
#
#     def calculate_fitness(self):
#         pop = Population(self.data)
#         pop.evolve()
#         return pop.get_best_genome().fitness
