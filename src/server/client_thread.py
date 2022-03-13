from threading import Thread, Lock

from src.common import Packet, PacketType
from src.common.channel import Channel
from src.common.config import ENCODING
from src.common.status_codes import SignInStatus
from .client import Client
from .connection_context import ConnectionContext
from .server_logger import LOG


class ClientThread():
    def __init__(self, channel: Channel, ctx: ConnectionContext) -> None:
        self.__thread = Thread(target=lambda: self.__thread_func(), daemon=True)
        self.__channel = channel
        self.__client = None
        self.__ctx = ctx

    def run(self):
        self.__thread.start()

    def __perform_handshake(self):
        LOG.info('Performing client hand-shake...')

        packet_type = self.__channel.receive_packet_header()
        if packet_type != PacketType.SIGN_IN:
            LOG.error('Client hand-shake failed. Expected SIGN_IN packet ' +
                      f'(type {PacketType.SIGN_IN.value}). Got {packet_type}')
            return False
        
        username = str(self.__channel.receive_var_len(), encoding=ENCODING)
        client = Client(username, self.__channel)

        # Letting others know
        if self.__ctx.register_client(client) == False:
            LOG.info(f'A duplicate username: \'{username}\'.')

            # Sending error response
            packet = Packet(PacketType.SIGN_IN)
            packet.append_bytes(bytes([SignInStatus.USED_USERNAME.value]))
            client.send(packet)
            return

        LOG.info(f'Hand-shake successful. \'{username}\' connected!')
        self.__client = client

        # Sending success response
        packet = Packet(PacketType.SIGN_IN)
        packet.append_bytes(bytes([SignInStatus.OK.value]))
        self.__client.send(packet)

        return True

    def __handle_message_packet(self):
        msg = str(self.__channel.receive_var_len(), encoding=ENCODING)

        LOG.info(f"({self.__client.username}): {msg}")

        packet = Packet(PacketType.MESSAGE)
        packet.append_var_len(bytes(msg, encoding=ENCODING))
        packet.append_var_len(bytes(self.__client.username, encoding=ENCODING))
        self.__ctx.send_to_all_except(packet, self.__client)

    def __thread_func(self):
        try:
            while not self.__perform_handshake():
                pass

            # Handling unprompted messages
            while True:
                packet_type = self.__client.try_retrieve()
                if packet_type is None:
                    continue

                LOG.debug(f'Got unprompted message of type {packet_type}')
                if packet_type == PacketType.MESSAGE:
                    self.__handle_message_packet()
                else:
                    LOG.error(f"Unhandled unprompted message of type {packet_type}")
        except ConnectionResetError:
            self.__channel.close()

            if self.__client is not None:
                self.__ctx.unregister_client(self.__client)
                LOG.info(f"User '{self.__client.username}' left.")
            else:
                LOG.info(f"Unregistered user left.")
        except OSError as e:
            # This is called when trying to write to a closed socket.
            # Usually happens at the end of this thread's lifetime
            pass

