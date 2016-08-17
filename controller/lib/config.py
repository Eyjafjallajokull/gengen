from os import getenv
import yaml
config = None


def read_config(path):
    global config
    config = yaml.load(open(path))
    config['main']['configPath'] = path
    config['pool_size'] = getenv('POOL_SIZE', 1)
    config['debug'] = True if getenv('DEBUG') else False
    return config
