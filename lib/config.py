import yaml
config = None

def readConfig(path):
    global config
    config = yaml.load(open(path))
    config['main']['configPath'] = path
    return config