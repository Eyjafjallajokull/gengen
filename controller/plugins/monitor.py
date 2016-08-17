import json
from lib import db
from numpy import std, average
from time import time

_time_run = time()
_time_generation = None


def register(population):
    population.add_event_listener('calculatedFitness', save_stats)


def save_stats(event):
    population = event.data['population']
    best_genome = population.get_best_genome()
    # average_fitness = reduce(lambda avg, g: avg + g.fitness, population.genomes, 0) / len(population.genomes)
    fitness_values = [g.fitness for g in population.genomes]
    average_fitness = average(fitness_values)
    std_fitness = std(fitness_values)
    genomes = [{"serial": g.serial, "fitness": g.fitness, "pngPath": g.pngPath} for g in population.genomes]
    duration_run = int(time() - _time_run)
    global _time_generation
    if _time_generation:
        duration_generation = int(time() - _time_generation)
    else:
        duration_generation = 0
    _time_generation = time()

    db.save('generation', population.generation)
    db.save('best_genome', best_genome.serial)
    db.save('best_fitness', best_genome.fitness)
    db.save('average_fitness', average_fitness)
    db.save('std_fitness', std_fitness)
    db.save('genomes', json.dumps(genomes))
    db.save('duration_run', duration_run)
    db.save('duration_generation', duration_generation)
