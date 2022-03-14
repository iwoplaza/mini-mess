import yaml

CONFIG_MAP = yaml.safe_load(open('config.yml'))
HOST = CONFIG_MAP['host']
PORT = CONFIG_MAP['port']
ENCODING = CONFIG_MAP['encoding']

MULTICAST_GROUP = CONFIG_MAP['multicast_group']
MULTICAST_PORT = CONFIG_MAP['multicast_port']
MULTICAST_TTL = CONFIG_MAP['multicast_ttl']
