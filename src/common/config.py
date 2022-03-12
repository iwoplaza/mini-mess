import yaml

CONFIG_MAP = yaml.safe_load(open('config.yml'))
HOST = CONFIG_MAP['host']
PORT = CONFIG_MAP['port']
ENCODING = CONFIG_MAP['encoding']
