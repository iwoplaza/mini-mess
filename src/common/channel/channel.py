from src.common.packet import Packet, PacketType


class Channel:
    def __init__(self, sock):
        self.sock = sock

        self.__recv_buffer = b''
        self.__last_address = None

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

    def send_packet_to(self, packet: Packet, address):
        msg = packet.get_bytes()

        totalsent = 0
        while totalsent < len(msg):
            sent = self.sock.sendto(msg[totalsent:], address)
            if sent == 0:
                raise RuntimeError('Socket connection broken')
            totalsent = totalsent + sent

    def __pop_bytes(self, amount: int) -> bytes:
        result = b''

        # Getting leftovers from the previous pull
        amount_in_buffer = min(amount, len(self.__recv_buffer))
        result += self.__recv_buffer[:amount_in_buffer]
        self.__recv_buffer = self.__recv_buffer[amount_in_buffer:]

        # Getting new bytes if necessary
        left = amount - amount_in_buffer
        if left > 0:
            self.__recv_buffer, self.__last_address = self.sock.recvfrom(1024)
            result += self.__recv_buffer[:left]
            self.__recv_buffer = self.__recv_buffer[left:]

        return result

    def get_datagram_address(self):
        return self.__last_address

    def receive_packet_header(self):
        # buffer = self.sock.recv(1)
        buffer = self.__pop_bytes(1)
        return PacketType(int.from_bytes(buffer, byteorder='little', signed=False))

    def receive_var_len(self) -> bytes:
        len_buffer = self.__pop_bytes(1)
        length = int.from_bytes(len_buffer, byteorder='little', signed=False)

        return self.receive_fixed_len(length)

    def receive_fixed_len(self, length: int) -> bytes:
        chunks = []
        bytes_recd = 0
        while bytes_recd < length:
            chunk = self.__pop_bytes(min(length - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError('Socket connection broken')
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)

        return b''.join(chunks)

    def with_timeout(self, callback, secs: float = 0.2):
        self.sock.settimeout(secs)
        callback()
        self.sock.settimeout(None)

