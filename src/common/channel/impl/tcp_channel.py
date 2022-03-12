from ..channel import Channel
from src.common.packet import Packet
from src.common.packet_types import PacketType


class TCPChannel(Channel):
    def __init__(self, sock):
        self.sock = sock

    def close(self):
        self.sock.close()

    def send_packet(self, packet: Packet):
        msg = packet.get_bytes()

        totalsent = 0
        while totalsent < len(msg):
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError('Socket connection broken')
            totalsent = totalsent + sent

    def receive_packet_header(self):
        buffer = self.sock.recv(1)
        return PacketType(int.from_bytes(buffer, byteorder='little', signed=False))

    def receive_var_len(self) -> bytes:
        len_buffer = self.sock.recv(1)
        length = int.from_bytes(len_buffer, byteorder='little', signed=False)

        return self.receive_fixed_len(length)

    def receive_fixed_len(self, length: int) -> bytes:
        chunks = []
        bytes_recd = 0
        while bytes_recd < length:
            chunk = self.sock.recv(min(length - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError('Socket connection broken')
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)

        return b''.join(chunks)
