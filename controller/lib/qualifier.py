import zerorpc


class DistributedQualifier(object):
    def calculate(self, base, target):
        c = zerorpc.Client()
        c.connect("tcp://qualifier:4242")
        result = c.qualify(base, target)
        c.close()
        return float(result)

