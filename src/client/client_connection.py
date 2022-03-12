import re
import socket
import time
from threading import Thread, Lock
from src.client.client_logger import LOG

from src.common.channel import TCPChannel
from src.common.packet import Packet
from src.common.packet_types import PacketType
from src.common.config import ENCODING, HOST, PORT
from src.common.status_codes import SignInStatus


USERNAME_REGEX = '^[A-Za-z0-9_]+$'

class ClientConnection:
    def __init__(self, on_message) -> None:
        self.__on_message = on_message
        self.__username = ''
        # Used when communicating back-and-forth.
        # Problems without it include:
        #   - Having the listening thread catch the response to a prompted dialog.
        self.__comm_lock = Lock()

    def sign_in(self, username: str):
        if not re.match(USERNAME_REGEX, username):
            raise RuntimeError('Username has to consist of letters, digits, and _')
        self.__username = username
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))

        self.__channel = TCPChannel(s)
        packet = Packet(PacketType.SIGN_IN)
        packet.append_var_len(bytes(self.__username, ENCODING))
        self.__channel.send_packet(packet)

        # Waiting for response
        response_type = self.__channel.receive_packet_header()
        if response_type != PacketType.SIGN_IN:
            raise RuntimeError('Got invalid response from the server. Please try again, or contact the administrator.')
        status = SignInStatus(int.from_bytes(self.__channel.receive_fixed_len(1), byteorder='little'))
        if status != SignInStatus.OK:
            raise RuntimeError('Got error: {status}')

        # Booting-up the listening thread
        self.__listening_thread = Thread(target=lambda: self.__listening_thread_func(), daemon=True)
        self.__listening_thread.start()

    def send_message(self, text: str):
        LOG.debug(f'Trying to send message {text}...')

        self.__comm_lock.acquire()
        LOG.debug(f'<send_message: Lock aquired>')
        try:
            self.__on_message(text, self.__username)

            packet = Packet(PacketType.MESSAGE)
            packet.append_var_len(bytes(text, encoding=ENCODING))
            self.__channel.send_packet(packet)
        finally:
            LOG.debug(f'<send_message: Lock released>')
            self.__comm_lock.release()

    def __listening_thread_func(self):
        LOG.debug('Booted up the listening thread')

        while True:
            # Waiting for unprompted message
            self.__comm_lock.acquire()
            LOG.debug(f'<thread: Lock aquired>')
            try:
                self.__channel.sock.settimeout(0.2)
                packet_type = self.__channel.receive_packet_header()
                self.__channel.sock.settimeout(None)

                LOG.debug(f'Got unprompted message of type {packet_type}')
                if packet_type == PacketType.MESSAGE:
                    msg = str(self.__channel.receive_var_len(), encoding=ENCODING)
                    sender = str(self.__channel.receive_var_len(), encoding=ENCODING)
                    self.__on_message(msg, sender)
                elif packet_type == PacketType.USER_JOINED:
                    username = str(self.__channel.receive_var_len(), encoding=ENCODING)
                    self.__on_message(f"{username} joined!", None)
                elif packet_type == PacketType.USER_LEFT:
                    username = str(self.__channel.receive_var_len(), encoding=ENCODING)
                    self.__on_message(f"{username} left!", None)
                else:
                    LOG.error("Unhandled unprompted message of type {packet_type}")
            except socket.timeout:
                pass
            finally:
                LOG.debug(f'<thread: Lock released>')
                self.__comm_lock.release()
                time.sleep(0.2) # Sleeping to let other threads aquire the lock
