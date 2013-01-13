import yaml
config = None

def readConfig(path):
    global config
    config = yaml.load(open(path))
    config['main']['configPath'] = path
    config['main']['logPath'] = path.replace('.yml', '.log')
    return config