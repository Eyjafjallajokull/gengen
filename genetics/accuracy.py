import copy
class AccuracyParam:
    def __init__(self, name, cfg, realValue):
        self.name = name
        self.multiplier = cfg['multiplier']
        self.minimum = cfg['minimum']
        self.scaledValue = float(realValue)
        self.realValue = realValue
        if 'int' in cfg:
            self.cast = int
        else:
            self.cast = float
        self.realIntSteps = False

    def getNextValue(self):
        realValue = self.realValue
        scaledValue = self.scaledValue
        if self.realIntSteps:
            while realValue == self.realValue:
                scaledValue *= self.multiplier
                realValue = self.cast(scaledValue)
        else:
            scaledValue *= self.multiplier
            realValue = self.cast(scaledValue)
        return (realValue, scaledValue)

    def canIncrease(self):
        (real, scaled) = self.getNextValue()
        return self.minimum < real

    def increase(self):
        if not self.canIncrease():
            return
        (real, scaled) = self.getNextValue()
        self.realValue = real
        self.scaledValue = scaled

class AccuracyMachine:
    def __init__(self, cfg, log):
        self.cfg = cfg
        self.log = log
        self.params = []
        self.genomeGenerationTrigger = cfg['accuracy']['trigger']
        if 'accuracy' in cfg:
            for paramName, paramConfig in cfg['accuracy'].items():
                if paramName != 'trigger':
                    param = AccuracyParam(paramName, paramConfig,
                        self.cfg['ga'][paramName])
                    self.params.append(param)
            self.maximumAccuracy = False
        else:
            self.maximumAccuracy = True

    def canIncrease(self):
        for param in self.params:
            if param.canIncrease():
                return True
        return False

    def increase(self):
        for param in self.params:
            old = param.realValue
            param.increase()
            self.cfg['ga'][param.name] = param.realValue
            if old != param.realValue:
                self.log.info('changed %s to %f'%(param.name, float(param.realValue)))

    def checkPopulation(self, population):
        if population.getBestGenome().generation >= self.genomeGenerationTrigger:
            return self.canIncrease()
        return False

    def checkBeforeEnd(self):
        return self.canIncrease()