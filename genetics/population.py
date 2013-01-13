import glob
from multiprocessing import Pool
from time import time
import pickle
import random
from lib.common import do
from lib.event import Event, EventDispatcher
import lib.log as log
import lib.config as config

def _poolFitnessCalculation(params):
    (fitnessMachine, genome) = params
    try:
        fitness = fitnessMachine.calculate(genome)
        genome.setFitness(fitness)
    except KeyboardInterrupt: pass
    return genome


class Population(EventDispatcher):
    def __init__(self, genomeType, fitnessMachine):
        super(Population, self).__init__()
        self.pool = Pool(processes=4, maxtasksperchild=100)
        self.generation = 0
        self.genomeType = genomeType
        self.genomes = []
        self.fitnessMachine = fitnessMachine

    def _dispatch_event(self, type):
        self.dispatch_event(Event(type, data={'population':self}))

    def load(self):
        genomeFiles = glob.glob(config.config['main']['populationRamPath'] + '*_genome.obj')
        if len(genomeFiles)==0:
            raise Exception('no genomes found under '+config.config['main']['populationRamPath'])
        for file in genomeFiles:
            genome = pickle.load(open(file))
            self.genomes.append(genome)
        log.info('loaded %d genomes' % len(self.genomes))

    def initialize(self):
        do('rm -f %s/*' % config.config['main']['populationRamPath'])
        do('mkdir %s' % config.config['main']['populationPath'])
        do('echo > %s' % config.config['main']['logPath'])
        for i in range(0, config.config['ga']['populationSize']):
            genome = self.genomeType()
            genome.create()
            self.genomes.append(genome)
        log.info('initialized population of %d genomes' % config.config['ga']['populationSize'])

    def step(self):
        self._dispatch_event('stepStart')
        log.info('SUNRISE %d generation' % self.generation)
        start = time()
        self.calculateFitness()
        self._dispatch_event('calculatedFitness')

        bestGenome = self.getBestGenome()
        log.debug('current population ' + ', '.join(map(lambda a: a.serial + '-' + str(a.fitness), self.genomes)))
        log.info('best genome %s-%d; average fitness %d'
                 % (bestGenome.serial, bestGenome.fitness,reduce(lambda avg, g: avg + g.fitness, self.genomes, 0) / len(self.genomes)))
        log.debug('genomeSize=%d' % config.config['ga']['genomeSize'])

        parents = self.selection()
        self.crossover(parents)
        log.info('%d s' % int(time() - start))
        self._dispatch_event('stepEnd')

    def calculateFitness(self):
        log.debug('calculateFitness')
        poolData = [[self.fitnessMachine, g] for g in self.genomes]
        timeout = 5 * config.config['ga']['populationSize']*10000
        self.genomes = self.pool.map_async(_poolFitnessCalculation, poolData).get(timeout)

    def selection(self):
        selectedGenomes = self._selectionTournament()
        #selectedGenomes = sorted(selectedGenomes, cmp=lambda a, b: cmp(a.fitness, b.fitness))
        log.debug('selected %d genomes: %s' %
                  (len(selectedGenomes), ', '.join(map(lambda a: a.serial + '-' + str(a.fitness), selectedGenomes))))
        return selectedGenomes

    def _selectionTournament(self):
        random.shuffle(self.genomes)
        groupSize = int(len(self.genomes) * config.config['ga']['selectionMultiplier'])
        selectedGenomes = []
        for i in range(0, len(self.genomes), groupSize):
            if len(self.genomes) < i + groupSize:
                end = len(self.genomes) - 1
            else:
                end = i + groupSize
            bestGenome = self.genomes[i]
            for genome in self.genomes[i + 1:end]:
                if bestGenome.fitness > genome.fitness:
                    bestGenome = genome
            selectedGenomes.append(bestGenome)
        return selectedGenomes

#    def _selectionProportionate(self):
#        howManyToSelect = int(len(self.genomes) * config.config['ga']['selectionMultiplier']) + 1
#        fitnessSum = map(lambda sum, genome: sum + genome.fitness, self.genomes)
#        selectedGenomes = []
#        for genome in self.genomes:
#            genome.normalizedFitness = genome.fitness / fitnessSum
#            #self.genomes = sorted(self.genomes, cmp=lambda a,b: cmp(a.normalizedFitness, b.normalizedFitness))
#        for i in range(0, howManyToSelect):
#            R = random.random()
#            for genome in self.genomes:
#                if genome.normalizedFitness > R:
#                    selectedGenomes.append(genome)
#                    break
#
#    def _selectionTruncation(self):
#        slice = int(len(self.genomes) * config.config['ga']['selectionMultiplier']) + 1
#        selectedGenomes = self.genomes[0:slice]
#        return selectedGenomes

    def crossover(self, parents):
        log.debug('crossover')
        if config.config['ga']['crossoverAllNew'] == 1:
            log.info('clear population')
            for genome in self.genomes:
                genome.remove()
            self.genomes = []
        else:
            for genome in self.genomes:
                if not genome in parents:
                    genome.remove()
            self.genomes = parents
        for i in range(0, config.config['ga']['populationSize'] - len(self.genomes)):
            (genomeA, genomeB) = (random.choice(parents), random.choice(parents))
            genomeC = self.genomeType()
            genomeC.createWithCrossover(genomeA, genomeB)
            genomeC.mutate()
            self.genomes.append(genomeC)

    def getBestGenome(self):
        best = self.genomes[0]
        for genome in self.genomes:
            if genome.fitness < best.fitness:
                best = genome
        return best

    def resetGeneration(self):
        log.info('resetGeneration')
        self.generation = 0
        for genome in self.genomes:
            genome.generation = 0

    def evolve(self):
        while self.generation < config.config['ga']['generations']:
            self.step()
            for genome in self.genomes:
                genome.generation += 1
                genome.save()
            self.generation += 1
            if self.generation == config.config['ga']['generations']:
                self._dispatch_event('lastGeneration')