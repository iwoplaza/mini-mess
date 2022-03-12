import socket
from threading import Lock

from src.common import Packet
from src.common.channel import Channel

class Client:
    def __init__(self, username: str, channel: Channel) -> None:
        self.username = username
        self.__channel = channel

        # Used when communicating back-and-forth.
        # Problems without it include:
        #   - Having the listening thread catch the response to a prompted dialog.
        self.__comm_lock = Lock()

    def send(self, packet: Packet):
        self.__comm_lock.acquire()
        try:
            self.__channel.send_packet(packet)
        finally:
            self.__comm_lock.release()

    def try_retrieve(self, timeout=0.2):
        self.__comm_lock.acquire()

        try:
            self.__channel.sock.settimeout(timeout)
            packet_type = self.__channel.receive_packet_header()
            self.__channel.sock.settimeout(None)

            return packet_type
        except socket.timeout:
            return None
        finally:
            self.__comm_lock.release()
