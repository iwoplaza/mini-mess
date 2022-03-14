import re
import socket
import time
from threading import Thread, Lock, Condition

from src.client.client_logger import LOG
from src.client.client_mode import ClientMode
from src.client.udp_listener import UDPListener
from src.common.channel import Channel
from src.common.packet import Packet, PacketType
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

        self.__mode = ClientMode.CONNECTING
        self.__mode_cv = Condition()

    def __connect(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, PORT))
            self.__channel = Channel(s)
        except ConnectionRefusedError:
            return False

        return True

    def __connection_thread_func(self):
        LOG.debug('Booted up the connection thread')

        while True:
            with self.__mode_cv:
                if self.__mode == ClientMode.CONNECTING:
                    LOG.info('Connecting...')
                    while self.__connect() == False:
                        LOG.info("Failed. Trying again in 5 seconds...")
                        time.sleep(5)
                    
                    self.__mode = ClientMode.SIGNING_IN

                    # Welcome message
                    LOG.info(
                        "<> WELCOME TO MINI-MESS! <>\n" +
                        "===========================\n" +
                        "Put in your username below\n"
                    )
                elif self.__mode == ClientMode.SIGNING_IN:
                    self.__mode_cv.wait_for(lambda: self.__mode != ClientMode.SIGNING_IN)
                elif self.__mode == ClientMode.CHAT:
                    # Waiting for unprompted message
                    self.__comm_lock.acquire()
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
                        elif packet_type == PacketType.SERVER_SHUTDOWN:
                            raise ConnectionResetError()
                        else:
                            LOG.error(f"Unhandled unprompted message of type {packet_type}")
                    except socket.timeout:
                        pass
                    except ConnectionResetError:
                        LOG.info('Disconnected from server')
                        self.__mode = ClientMode.CONNECTING
                    finally:
                        self.__comm_lock.release()
            
            time.sleep(0.2) # Sleeping to let other threads aquire the lock

    def run(self):
        self.__thread = Thread(target=lambda: self.__connection_thread_func(), daemon=True)
        self.__thread.start()

    def sign_in(self, username: str):
        if not re.match(USERNAME_REGEX, username):
            raise RuntimeError('Username has to consist of letters, digits, and _')
        self.__username = username
        
        packet = Packet(PacketType.SIGN_IN)
        packet.append_var_len(bytes(self.__username, ENCODING))

        try:
            self.__channel.send_packet(packet)
        except ConnectionResetError:
            with self.__mode_cv:
                self.__mode = ClientMode.CONNECTING
                self.__mode_cv.notify()
            raise RuntimeError('Disconnected')

        # Waiting for response
        response_type = self.__channel.receive_packet_header()
        if response_type != PacketType.SIGN_IN:
            raise RuntimeError('Got invalid response from the server. Please try again, or contact the administrator.')
        status = SignInStatus(int.from_bytes(self.__channel.receive_fixed_len(1), byteorder='little'))
        if status != SignInStatus.OK:
            if status == SignInStatus.USED_USERNAME:
                raise RuntimeError('The username is already taken.')
            else:
                raise RuntimeError(f'Got error: {status}')

        with self.__mode_cv:
            self.__mode = ClientMode.CHAT
            self.__mode_cv.notify()

    def send_message(self, text: str):
        LOG.debug(f'Trying to send message {text}...')

        self.__comm_lock.acquire()
        try:
            self.__on_message(text, self.__username)

            packet = Packet(PacketType.MESSAGE)
            packet.append_var_len(bytes(text, encoding=ENCODING))
            self.__channel.send_packet(packet)
        finally:
            self.__comm_lock.release()

    def get_mode(self):
        with self.__mode_cv:
            return self.__mode

    def get_username(self):
        return self.__username
