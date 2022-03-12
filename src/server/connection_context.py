from threading import Lock

from src.common import Packet, PacketType
from src.common.config import ENCODING
from .client import Client


class ConnectionContext:
    def __init__(self) -> None:
        self.__client_dict = dict()
        self.__mutex = Lock()

    def register_client(self, client: Client):
        self.__mutex.acquire()
        try:
            self.__client_dict[client.username] = client
        finally:
            self.__mutex.release()

        packet = Packet(PacketType.USER_JOINED)
        packet.append_var_len(bytes(client.username, encoding=ENCODING))
        self.send_to_all_except(packet, client)

    def send_to_all(self, packet):
        self.__mutex.acquire()

        try:
            for (_, c) in self.__client_dict.items():
                c.send(packet)
        finally:
            self.__mutex.release()

    def send_to_all_except(self, packet, exception: Client):
        self.__mutex.acquire()

        try:
            for (_, c) in self.__client_dict.items():
                if c != exception:
                    c.send(packet)
        finally:
            self.__mutex.release()
