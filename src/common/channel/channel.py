from src.common import Packet


class Channel:
    def close(self):
        raise NotImplementedError()

    def send_packet(self, packet: Packet):
        raise NotImplementedError()

    def receive_packet_header(self):
        raise NotImplementedError()

    def receive_var_len(self) -> bytes:
        raise NotImplementedError()

    def receive_fixed_len(self, length: int) -> bytes:
        raise NotImplementedError()

