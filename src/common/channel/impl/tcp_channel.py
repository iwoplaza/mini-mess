import socket

from ..channel import Channel
from src.common.packet_types import PacketType


class TCPChannel(Channel):
    def __init__(self, host, port, encoding='cp1250'):
        self.encoding = encoding
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.client.connect((host, port))

    def close(self):
        self.client.close()

    def send_packet(self, packet_type: PacketType, content: bytes):
        type_header = packet_type.value.to_bytes(1, byteorder='little', signed=False)

        self.client.send(type_header + content)

    def receive_packet_header(self):
        buffer = self.client.recv(1)
        return int.from_bytes(buffer, byteorder='little', signed=False)

    def receive_var_len(self) -> bytes:
        len_buffer = self.client.recv(1)
        length = int.from_bytes(len_buffer, byteorder='little', signed=False)

        return self.receive_fixed_len(length)

    def receive_fixed_len(self, length: int) -> bytes:
        chunks = []
        bytes_recd = 0
        while bytes_recd < length:
            chunk = self.client.recv(min(length - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError('Socket connection broken')
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)

        return b''.join(chunks)