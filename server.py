import socket
from src.common import Packet, PacketType
from src.common.channel import Channel
from src.common.config import PORT

from src.server import LOG, ClientThread
from src.server.connection_context import ConnectionContext
from src.server.udp_thread import UDPThread

def main():
    LOG.info('== MINI-MESS Server')
    LOG.info('===================')

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.settimeout(0.2)
    server_socket.bind(('', PORT))
    server_socket.listen(5)

    connection_ctx = ConnectionContext()

    # Running the UDP listening thread.
    try:
        udp_thread = UDPThread(connection_ctx)

        while True:
        # Accept connections from the outside
            try:
                (clientsocket, address) = server_socket.accept()
                ct = ClientThread(Channel(clientsocket), udp_thread.channel, connection_ctx)
                ct.run()
            except socket.timeout:
                pass
    except KeyboardInterrupt:
        pass

    # Disconnecting all clients
    packet = Packet(PacketType.SERVER_SHUTDOWN)
    connection_ctx.send_to_all(packet)
    connection_ctx.close_all()

    print('Exiting...')

if __name__ == '__main__':
    main()
