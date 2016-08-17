import lib.config as config
import math
import lib.log as log


def register(population):
    accuracy_machine = AccuracyPlugin()
    population.add_event_listener('calculatedFitness', accuracy_machine.onCalculatedFitness)
    population.add_event_listener('lastGeneration', accuracy_machine.onLastGeneration)


class AccuracyPlugin:
    def __init__(self):
        self.params = []
        if 'accuracy' in config.config:
            self.genomeGenerationTrigger = config.config['accuracy']['trigger']
            for paramName, paramConfig in config.config['accuracy'].items():
                if paramName != 'trigger':
                    param = AccuracyParam(paramName, paramConfig, config.config['ga'][paramName])
                    self.params.append(param)
            self.maximumAccuracy = False
            self.active = True
        else:
            self.maximumAccuracy = True
            self.active = False

    def canIncrease(self):
        for param in self.params:
            if param.canIncrease():
                return True
        return False

    def increase(self):
        for param in self.params:
            old = param.currentValue
            param.increase()
            config.config['ga'][param.name] = param.currentValue
            if old != param.currentValue:
                log.info('changed %s from %s to %s'%(param.name, str(old), str(param.currentValue)))
                if param.name == 'genomeSize':
                    for param2 in self.params:
                        if param2.name != 'genomeSize':
                            param2.resetToOriginalValue()
                    log.info('genomeSize change triggered resetting of the other params')
                    break

    def onCalculatedFitness(self, event):
        pop = event.data['population']
        if self.active and pop.get_best_genome().generation >= self.genomeGenerationTrigger and self.canIncrease():
            self.increase()
            pop.reset_generation()

    def onLastGeneration(self, event):
        pop = event.data['population']
        if self.active and self.canIncrease():
            self.increase()
            pop.reset_generation()


class AccuracyParam:
    def __init__(self, name, cfg, currentValue):
        self.name = name
        self.multiplier = cfg['multiplier']
        self.minimum = cfg['minimum'] if 'minimum' in cfg else None
        self.maximum = cfg['maximum'] if 'maximum' in cfg else None
        self.originalValue = currentValue
        self.resetToOriginalValue()
        if 'int' in cfg and cfg['int']==1:
            self.cast = lambda x: int(math.ceil(x))
        else:
            self.cast = float

    def __repr__(self):
        return self.name+'_'+str(self.currentValue)+'_'+str(self.scaledValue)

    def resetToOriginalValue(self):
        self.scaledValue = float(self.originalValue)
        self.currentValue = self.originalValue

    def getNextValue(self):
        scaledValue = self.scaledValue * self.multiplier
        currentValue = self.cast(scaledValue)
        return (currentValue, scaledValue)

    def canIncrease(self):
        (current, _) = self.getNextValue()
        if self.minimum != None:
            return self.minimum < current
        if self.maximum != None:
            return self.maximum > current
        return True

    def increase(self):
        if not self.canIncrease():
            return
        (current, scaled) = self.getNextValue()
        self.currentValue = current
        self.scaledValue = scaled
