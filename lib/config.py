import yaml

def readConfig(path):
    return yaml.load(open(path))