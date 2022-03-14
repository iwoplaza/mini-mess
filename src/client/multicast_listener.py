import socket
import struct
import time
from threading import Thread, Lock

from src.client.client_logger import LOG
from src.common.channel import Channel
from src.common.packet import Packet, PacketType
from src.common.config import ENCODING, MULTICAST_GROUP, MULTICAST_PORT, MULTICAST_TTL


class MulticastListener:
    def __init__(self, on_message) -> None:
        self.__on_message = on_message
        self.__username = ''
        # Used when communicating back-and-forth.
        # Problems without it include:
        #   - Having the listening thread catch the response to a prompted dialog.
        self.__comm_lock = Lock()

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', MULTICAST_PORT))

        membership = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)

        self.__channel = Channel(s)

        self.__thread = Thread(target=self.__thread_func, daemon=True)
        self.__thread.start()

    def __thread_func(self):
        LOG.debug('Booted up the Multicast listening thread')

        while True:
            # Waiting for unprompted message
            self.__comm_lock.acquire()
            try:
                self.__channel.sock.settimeout(0.2)
                packet_type = self.__channel.receive_packet_header()
                self.__channel.sock.settimeout(None)

                LOG.debug(f'Got unprompted Multicast message of type {packet_type}')
                if packet_type == PacketType.MESSAGE:
                    msg = str(self.__channel.receive_var_len(), encoding=ENCODING)
                    sender = str(self.__channel.receive_var_len(), encoding=ENCODING)
                    self.__on_message(msg, sender)
                else:
                    LOG.error(f"Unhandled unprompted Multicast message of type {packet_type}")
            except socket.timeout:
                pass
            finally:
                self.__comm_lock.release()
            
            time.sleep(0.2) # Sleeping to let other threads aquire the lock

    def set_username(self, username):
        self.__username = username

    def run(self):
        self.__thread = Thread(target=lambda: self.__thread_func(), daemon=True)
        self.__thread.start()

    def send_message(self, text: str):
        LOG.debug(f'Trying to send Multicast message {text}...')

        with self.__comm_lock:
            try:
                packet = Packet(PacketType.MESSAGE)
                packet.append_var_len(bytes(text, encoding=ENCODING))
                packet.append_var_len(bytes(self.__username, encoding=ENCODING))
                self.__channel.send_packet_to(packet, (MULTICAST_GROUP, MULTICAST_PORT))
            except OSError as e:
                LOG.error(f'Failed to send Multicast message. Reason: {e}')
