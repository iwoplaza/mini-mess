from .packet_types import PacketType

class Packet:
    def __init__(self, packet_type: PacketType) -> None:
        self.__packet_type = packet_type
        self.__content = b''

    def append_bytes(self, more: bytes):
        self.__content += more

    def append_var_len(self, more: bytes):
        len_buffer = len(more).to_bytes(length=1, byteorder='little', signed=False)

        self.__content += len_buffer
        self.__content += more

    def get_bytes(self):
        encoded_type = self.__packet_type.value.to_bytes(1, byteorder='little', signed=False)

        return encoded_type + self.__content
