from __future__ import annotations

import libscrc_fake as libscrc

from grottdata import encrypt
from messages.response import Response
from messages.message import Message


class Command(Message):
    response: Response
    body: str
    device_id: int
    header: str

    @property
    def header(self):
        send_sequence = 1  # No idea what this means
        body_length = len(bytes.fromhex(self.body)) + 2  # Add two bytes for device id and record type.
        return f"{send_sequence:04x}00{self.protocol}{body_length:04x}{self.device_id:02x}{self.record_type:02x}"

    @property
    def data(self):
        return bytes.fromhex(self.header + self.body)

    @property
    def raw(self):
        raw = self.data
        if self.protocol != "02":
            encrypted = encrypt(self.data)
            crc16 = libscrc.modbus(bytes.fromhex(encrypted))
            raw = bytes.fromhex(encrypted) + crc16.to_bytes(2, "big")
        return raw
