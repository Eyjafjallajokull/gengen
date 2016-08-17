import glob
import pickle
import random
from multiprocessing import Pool, TimeoutError
from lib.common import do
from lib.event import Event, EventDispatcher
from lib.timer import Timer
import lib.log as log
import lib.config as config


def _pool_fitness_calculation(params):
    (fitness_machine, genome) = pickle.loads(params)
    fitness = None
    try:
        fitness = fitness_machine.calculate(genome)

    except KeyboardInterrupt:
        pass
    return fitness


class Population(EventDispatcher):
    def __init__(self, genome_type, fitness_machine):
        super(Population, self).__init__()
        self.pool = Pool(processes=5, maxtasksperchild=100)
        self.generation = 0
        self.genomeType = genome_type
        self.genomes = []
        self.fitnessMachine = fitness_machine

    def _dispatch_event(self, event_type):
        self.dispatch_event(Event(event_type, data={'population': self}))

    def load(self):
        genome_files = glob.glob(config.config['main']['populationPath'] + '*_genome.obj')
        if len(genome_files) == 0:
            raise Exception('no genomes found under '+config.config['main']['populationPath'])
        for genome_file in genome_files:
            try:
                genome = pickle.load(open(genome_file))
                self.genomes.append(genome)
            except EOFError:
                log.error("could not load genome from file %s" % genome_file)
        log.info('loaded %d genomes' % len(self.genomes))

    def initialize(self):
        do('rm -f %s/*' % config.config['main']['populationPath'])
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
        with Timer('Fitness calculated in %f', log.INFO):
            self.calculate_fitness()
        self._dispatch_event('calculatedFitness')

        best_genome = self.get_best_genome()
        log.debug('current population ' + ', '.join(map(lambda a: a.serial + '-' + str(a.fitness), self.genomes)))
        log.info('best genome %s-%d' % (best_genome.serial, best_genome.fitness))
        log.debug('genomeSize=%d' % config.config['ga']['genomeSize'])

        parents = self.selection()
        self.crossover(parents)
        self._dispatch_event('stepEnd')

    def calculate_fitness(self):
        log.debug('calculate_fitness')
        pool_data = [[self.fitnessMachine, g] for g in self.genomes]
        log.debug('pool_data: ' + str(pool_data))
        pool_data = [pickle.dumps((self.fitnessMachine, g)) for g in self.genomes]

        # self.genomes = [_poolFitnessCalculation(i) for i in pool_data]

        tmp = self.genomes
        soft_recovery = True
        try:
            fitness_values = self.pool.map_async(_pool_fitness_calculation, pool_data).get(timeout=30)
            for i, fitness in enumerate(fitness_values):
                self.genomes[i].set_fitness(fitness)
        except TimeoutError as e:
            if soft_recovery:
                self.genomes = tmp
                log.error('!!!!!!!!! ' + str(e))
            else:
                raise e

    def selection(self):
        selected_genomes = self._selection_tournament()
        # selected_genomes = sorted(selected_genomes, cmp=lambda a, b: cmp(a.fitness, b.fitness))
        log.debug('selected %d genomes: %s' %
                  (len(selected_genomes), ', '.join(map(lambda a: a.serial + '-' + str(a.fitness), selected_genomes))))
        return selected_genomes

    def _selection_tournament(self):
        random.shuffle(self.genomes)
        group_size = int(len(self.genomes) * config.config['ga']['selectionMultiplier'])
        selected_genomes = []
        for i in range(0, len(self.genomes), group_size):
            if len(self.genomes) < i + group_size:
                end = len(self.genomes) - 1
            else:
                end = i + group_size
            best_genome = self.genomes[i]
            for genome in self.genomes[i + 1:end]:
                if best_genome.fitness > genome.fitness:
                    best_genome = genome
            selected_genomes.append(best_genome)
        return selected_genomes

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
                if genome not in parents:
                    genome.remove()
            self.genomes = parents
        for i in range(0, config.config['ga']['populationSize'] - len(self.genomes)):
            (genome_a, genome_b) = (random.choice(parents), random.choice(parents))
            genome_c = self.genomeType()
            genome_c.create_with_crossover(genome_a, genome_b)
            genome_c.mutate()
            self.genomes.append(genome_c)

    def get_best_genome(self):
        best = self.genomes[0]
        for genome in self.genomes:
            if genome.fitness < best.fitness:
                best = genome
        return best

    def reset_generation(self):
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
