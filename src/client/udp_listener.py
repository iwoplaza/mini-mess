import socket
import time
from threading import Thread, Lock

from src.client.client_logger import LOG
from src.common.channel import Channel
from src.common.packet import Packet, PacketType
from src.common.config import ENCODING, HOST, PORT
from src.common.status_codes import SignInStatus


class UDPListener:
    def __init__(self, on_message) -> None:
        self.__on_message = on_message
        self.__username = ''
        # Used when communicating back-and-forth.
        # Problems without it include:
        #   - Having the listening thread catch the response to a prompted dialog.
        self.__comm_lock = Lock()

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__channel = Channel(s)

        self.__thread = Thread(target=self.__thread_func, daemon=True)
        self.__thread.start()

    def __thread_func(self):
        LOG.debug('Booted up the UDP listening thread')

        while True:
            # Waiting for unprompted message
            self.__comm_lock.acquire()
            try:
                self.__channel.sock.settimeout(0.2)
                packet_type = self.__channel.receive_packet_header()
                self.__channel.sock.settimeout(None)

                LOG.debug(f'Got unprompted UDP message of type {packet_type}')
                if packet_type == PacketType.MESSAGE:
                    msg = str(self.__channel.receive_var_len(), encoding=ENCODING)
                    sender = str(self.__channel.receive_var_len(), encoding=ENCODING)
                    self.__on_message(msg, sender)
                else:
                    LOG.error(f"Unhandled unprompted UDP message of type {packet_type}")
            except socket.timeout:
                pass
            finally:
                self.__comm_lock.release()
            
            time.sleep(0.2) # Sleeping to let other threads aquire the lock

    def run(self):
        self.__thread = Thread(target=lambda: self.__thread_func(), daemon=True)
        self.__thread.start()

    def send_message(self, text: str):
        LOG.debug(f'Trying to send UDP message {text}...')

        with self.__comm_lock:
            try:
                self.__on_message(text, self.__username)

                packet = Packet(PacketType.MESSAGE)
                packet.append_var_len(bytes(text, encoding=ENCODING))
                packet.append_var_len(bytes(self.__username, encoding=ENCODING))
                self.__channel.send_packet_to(packet, (HOST, PORT))
            except OSError as e:
                LOG.error(f'Failed to send UDP message. Reason: {e}')

    def establish_channel(self, username):
        with self.__comm_lock:
            self.__username = username

            packet = Packet(PacketType.SIGN_IN)
            packet.append_var_len(bytes(self.__username, ENCODING))

            try:
                self.__channel.send_packet_to(packet, (HOST, PORT))
            except ConnectionResetError:
                raise RuntimeError('Disconnected')

            # Waiting for response
            response_type = self.__channel.receive_packet_header()
            if response_type != PacketType.SIGN_IN:
                raise RuntimeError('Got invalid response from the server. Please try again, or contact the administrator.')
            status = SignInStatus(int.from_bytes(self.__channel.receive_fixed_len(1), byteorder='little'))
            if status != SignInStatus.OK:
                raise RuntimeError(f'Got error: {status}')

    def get_username(self):
        return self.__username
