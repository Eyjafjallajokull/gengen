import glob
from multiprocessing import Pool
from time import time
from termcolor import colored
import pickle
import random
from genetics.accuracy import AccuracyMachine
from lib.common import do
import lib.config as config

generation = lambda s: colored(s, 'yellow', attrs=['bold'])
stage = lambda s: colored(s, 'green', attrs=['bold'])
info = lambda s: colored(s, 'blue')

def _poolFitnessCalculation(params):
    (fitnessMachine, genome) = params
    try:
        fitness = fitnessMachine.calculate(genome)
        genome.setFitness(fitness)
    except KeyboardInterrupt: pass
    return genome


class Population():
    def __init__(self, genomeType, log):
        self.pool = Pool(processes=4, maxtasksperchild=100)
        self.generation = 0
        self.genomeType = genomeType
        self.genomes = []
        self.log = log
        self.fitnessMachine = None
        # todo: AccuracyMachine should listen for Population events
        self.accuracyMachine = AccuracyMachine(self.log)

    def load(self):
        genomeFiles = glob.glob(config.config['main']['populationRamPath'] + '*_genome.obj')
        if len(genomeFiles)==0:
            raise Exception('no genomes found under '+config.config['main']['populationRamPath'])
        for file in genomeFiles:
            genome = pickle.load(open(file))
            self.genomes.append(genome)

    def initialize(self):
        do('rm -f %s* tmp* cache*' % config.config['main']['populationRamPath'])
        do('mkdir %s' % config.config['main']['populationPath'])
        for i in range(0, config.config['ga']['populationSize']):
            genome = self.genomeType()
            genome.create()
            self.genomes.append(genome)
        self.log.info('created population of %d genomes' % config.config['ga']['populationSize'])

    def step(self):
        self.log.info(generation('SUNRISE %d generation' % self.generation))
        start = time()
        self.calculateFitness()

        self.genomes = sorted(self.genomes, cmp=lambda a, b: cmp(a.fitness, b.fitness))
        if self.accuracyMachine.checkPopulation(self):
            self.accuracyMachine.increase()
            self.resetGeneration()

        bestGenome = self.genomes[0]
        self.log.debug(
            info('current population ') + ', '.join(map(lambda a: a.serial + '-' + str(a.fitness), self.genomes)))
        self.log.info(info('best genome %s-%d; average fitness %d'
                           % (bestGenome.serial, bestGenome.fitness,
                              reduce(lambda avg, g: avg + g.fitness, self.genomes, 0) / len(self.genomes))))

        parents = self.selection()
        self.crossover(parents)
        self.log.info(generation('SUNSET %d seconds' % int(time() - start)))

    def calculateFitness(self):
        self.log.debug(info('calculateFitness'))
        poolData = [[self.fitnessMachine, g] for g in self.genomes]
        timeout = 5 * config.config['ga']['populationSize']*10000
        self.genomes = self.pool.map_async(_poolFitnessCalculation, poolData).get(timeout)

    def selection(self):
        selectedGenomes = self._selectionTournament()
        self.log.debug(stage('selected %d genomes' % (len(selectedGenomes))))
        selectedGenomes = sorted(selectedGenomes, cmp=lambda a, b: cmp(a.fitness, b.fitness))
        self.log.debug(', '.join(map(lambda a: a.serial + '-' + str(a.fitness), selectedGenomes)))
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
        self.log.debug(stage('crossover'))
        if config.config['ga']['crossoverAllNew'] == 1:
            self.log.info('clear population')
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
        self.genomes = sorted(self.genomes, cmp=lambda a, b: cmp(a.fitness, b.fitness))
        return self.genomes[0]

    def resetGeneration(self):
        self.log.info('resetGeneration')
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
            if self.generation == config.config['ga']['generations'] and self.accuracyMachine.checkBeforeEnd():
                self.accuracyMachine.increase()
                self.resetGeneration()
