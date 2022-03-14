import socket
from threading import Thread

from src.common.channel import Channel
from src.common.config import ENCODING, PORT
from src.common.packet import PacketType, MessagePacket, SignInResponse
from src.common.status_codes import SignInStatus
from .connection_context import ConnectionContext
from .server_logger import LOG


class UDPThread:
    def __init__(self, ctx: ConnectionContext) -> None:
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__socket.bind(('', PORT))
        self.channel = Channel(self.__socket)
        self.__ctx = ctx

        self.__thread = Thread(target=self.__thread_func, daemon=True)
        self.__thread.start()

    def __handle_message_packet(self):
        msg = str(self.channel.receive_var_len(), encoding=ENCODING)
        sender = str(self.channel.receive_var_len(), encoding=ENCODING)

        LOG.info(f"({sender}): {msg}")
        self.__ctx.send_udp_to_all_except(MessagePacket(msg, sender), sender)

    def __handle_signin_packet(self):
        username = str(self.channel.receive_var_len(), encoding=ENCODING)
        address = self.channel.get_datagram_address()

        self.__ctx.link_udp_channel(username, address)

        LOG.info(f'UDP link esablished with \'{username}\'.')

        # Sending success response
        self.channel.send_packet_to(SignInResponse(SignInStatus.OK), address)

    def __thread_func(self):
        while True:
            try:
                self.channel.sock.settimeout(0.2)
                packet_type = self.channel.receive_packet_header()
                self.channel.sock.settimeout(None)

                LOG.info(f"UDP Packet: {packet_type}")

                if packet_type == PacketType.MESSAGE:
                    self.__handle_message_packet()
                elif packet_type == PacketType.SIGN_IN:
                    self.__handle_signin_packet()
                else:
                    LOG.error(f"Unhandled UDP packet type: {packet_type}")
            except socket.timeout:
                pass
