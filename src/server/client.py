import socket
from threading import Lock

from src.common.packet import Packet
from src.common.channel import Channel
from src.server.server_logger import LOG

class Client:
    def __init__(self, username: str, channel: Channel, udp_channel: Channel) -> None:
        self.username = username
        self.__channel = channel
        self.__udp_channel = udp_channel
        self.__udp_address = None

        # Used when communicating back-and-forth.
        # Problems without it include:
        #   - Having the listening thread catch the response to a prompted dialog.
        self.__comm_lock = Lock()
        self.__udp_comm_lock = Lock()

    def close(self):
        self.__channel.close()

    def link_udp_channel(self, address):
        with self.__udp_comm_lock:
            self.__udp_address = address

    def send(self, packet: Packet):
        with self.__comm_lock:
            self.__channel.send_packet(packet)

    def send_udp(self, packet: Packet):
        with self.__udp_comm_lock:
            if self.__udp_address is None:
                LOG.warn(f'Tried to send UDP, without a UDP address bound to client "{self.username}".')
                return

            self.__udp_channel.send_packet_to(packet, self.__udp_address)

    def try_retrieve(self, timeout=0.2):
        with self.__comm_lock:
            try:
                self.__channel.sock.settimeout(timeout)
                packet_type = self.__channel.receive_packet_header()
                self.__channel.sock.settimeout(None)

                return packet_type
            except socket.timeout:
                return None
