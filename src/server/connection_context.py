from threading import Lock

from src.common import Packet, PacketType
from src.common.config import ENCODING
from .client import Client


class ConnectionContext:
    def __init__(self) -> None:
        self.__client_dict = dict()
        self.__mutex = Lock()

    def register_client(self, client: Client) -> bool:
        self.__mutex.acquire()
        try:
            if client.username in self.__client_dict:
                return False
            
            self.__client_dict[client.username] = client
        finally:
            self.__mutex.release()

        packet = Packet(PacketType.USER_JOINED)
        packet.append_var_len(bytes(client.username, encoding=ENCODING))
        self.send_to_all_except(packet, client)

        return True

    def unregister_client(self, client: Client):
        with self.__mutex:
            if client.username not in self.__client_dict:
                return
            
            del self.__client_dict[client.username]

        packet = Packet(PacketType.USER_LEFT)
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

    def close_all(self):
        with self.__mutex:
            for (_, c) in self.__client_dict.items():
                c.close()
