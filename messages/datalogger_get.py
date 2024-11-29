from __future__ import annotations

import codecs

from messages.command import Command
from messages.response import Response


class DataloggerGetCommand(Command):
    record_type = 25  # 0x19
    device_id = "01"  # Always 1 for datalogger

    def __init__(self, datalogger_id: str, register: int, protocol: str, response_format: str = "dec"):
        self.datalogger_id = datalogger_id
        self.register = register
        self.response_format = response_format
        self.protocol = protocol

    @property
    def body(self):
        body = self.datalogger_id.encode('utf-8').hex()  # Datalogger
        body += "0" * self.offset  # Pad with zeros
        body += f"{self.register:04x}"  # Register
        return body


class DataloggerGetResponse(Response):
    record_type = DataloggerGetCommand.record_type

    def __init__(self, data):
        super().__init__(data)
        value_length = int(self.data[40:44], base=16)
        self.value = codecs.decode(self.data[44:44 + value_length * 2], "hex")
        self.response = {"value": self.value}
