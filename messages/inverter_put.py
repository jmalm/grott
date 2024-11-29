from __future__ import annotations

import libscrc_fake as libscrc
from grottdata import encrypt

from messages.command import Command
from messages.response import Response


class InverterPutMultipleCommand(Command):
    record_type = 16  # 0x10
    buffer_length = 10  # number of words (2 bytes) between datalogger id and body

    def __init__(self, protocol: int, device_id: int, datalogger_id: bytes, start_register: int, end_register: int,
                 values: list[int], **kwargs):
        self.protocol = f"{protocol:02x}"
        self.device_id = device_id
        self.datalogger_id = datalogger_id
        self.start_register = start_register
        self.end_register = end_register
        self.values = values
        self._additional = kwargs

    @property
    def buffer(self):
        return int(0).to_bytes(2, byteorder="big") * self.buffer_length

    @property
    def body(self):
        return (self.datalogger_id +
                self.buffer +
                self.start_register.to_bytes(2, "big") +
                self.end_register.to_bytes(2, "big") +
                b"".join(value.to_bytes(2, "big") for value in self.values))

    def serialize(self):
        send_sequence = 1
        body_length = len(self.body) + 2  # Add two bytes for crc16
        header = f"{send_sequence:04x}00{self.protocol}{body_length:04x}{self.device_id:02x}{self.record_type:02x}"
        data = bytes.fromhex(header) + self.body  # TODO: Harmonize with Command and Message
        encrypted = encrypt(data, return_bytes=True)
        crc16 = libscrc.modbus(encrypted)
        return encrypted + crc16.to_bytes(2, "big")


class InverterPutResponse(Response):
    record_type = 6
    is_encrypted_ack = True
    offset = 40

    def __init__(self, data):
        super().__init__(data)
        self.result = self.get_data(40, 2)
        self.value = self.get_data(42, 4)
        self.response = {"value": self.value, "result": self.result}


class InverterPutMultipleResponse(Response):
    record_type = InverterPutMultipleCommand.record_type

    def __init__(self, data):
        super().__init__(data)
        self.value = self.data[84:86]  # TODO: why only two bytes?
        self.response = {"value": self.value}

    def register_key(self):
        start_register = int(self.data[76:80], base=16)
        end_register = int(self.data[80:84], base=16)
        return f"{start_register:04x}{end_register:04x}"
