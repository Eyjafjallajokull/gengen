import yaml
config = None

def readConfig(path):
    global config
    config = yaml.load(open(path))
    return config