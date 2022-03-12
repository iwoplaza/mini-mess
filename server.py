import socket
import yaml

from src.server import LOG, ClientThread
from src.common.channel import TCPChannel
from src.server.connection_context import ConnectionContext


LOG.info('== MINI-MESS Server')
LOG.info('===================')

config = yaml.safe_load(open("config.yml"))
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.settimeout(0.2)
server_socket.bind(('', config['port']))
server_socket.listen(5)

connection_ctx = ConnectionContext()

while True:
    # Accept connections from the outside
    try:
        try:
            (clientsocket, address) = server_socket.accept()
            ct = ClientThread(TCPChannel(clientsocket), connection_ctx)
            ct.run()
        except socket.timeout:
            pass
    except KeyboardInterrupt as e:
        break
    

print('Exiting...')
