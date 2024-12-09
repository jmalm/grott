from __future__ import annotations

from dataclasses import dataclass

from messages.ack import Ack
from messages.data_message import DataMessage


@dataclass(init=False)
class MultiRegisterMessage(DataMessage):
    """A message that specifies multiple registers."""
    start_register: int
    end_register: int

    def __init__(self, protocol: int, device_id: int, record_type: int,
                 datalogger_id: bytes, start_register: int, end_register: int, raw: bytes = None):
        """
        :param start_register: The first register.
        :param end_register: The last register. (Can be the same as start_register.)
        """
        super().__init__(protocol, device_id, record_type, datalogger_id, raw)
        self.start_register = start_register
        self.end_register = end_register

    @property
    def body(self) -> bytes:
        if self._body is not None:
            return self._body
        self._body = super().body
        self._body += self.start_register.to_bytes(2, "big")
        self._body += self.end_register.to_bytes(2, "big")
        return self._body

    @classmethod
    def deserialize(cls, raw: bytes) -> (MultiRegisterMessage, bytes):
        message, rest = super().deserialize(raw)
        if len(rest) < 4:
            raise ValueError(f"Expected two registers, got {rest}")
        try:
            start_register = int.from_bytes(rest[0:2], "big")
        except IndexError or ValueError:
            raise ValueError(f"Expected start register in first word of content, got {rest}")
        try:
            end_register = int.from_bytes(rest[2:4], "big")
        except IndexError or ValueError:
            raise ValueError(f"Expected end register in second word of content, got {rest}")
        return MultiRegisterMessage(message.protocol, message.device_id, message.record_type,
                                    message.datalogger_id, start_register, end_register, raw), rest[4:]


@dataclass(init=False)
class MultiRegisterAck(MultiRegisterMessage, Ack):

    def __init__(self, protocol: int, device_id: int, record_type: int, datalogger_id: bytes, start_register: int,
                 end_register: int, result: int, raw: bytes = None):
        super().__init__(protocol, device_id, record_type, datalogger_id, start_register, end_register, raw)
        self.result = result

    @property
    def body(self) -> bytes:
        return (super().body +
                self.result.to_bytes(1, "big"))

    @classmethod
    def deserialize(cls, raw: bytes) -> (MultiRegisterAck, bytes):
        message, rest = super().deserialize(raw)
        if len(rest) == 0:
            raise ValueError(f"Expected ack result, got {rest}")
        result = rest[0]
        return MultiRegisterAck(message.protocol, message.device_id, message.record_type, message.datalogger_id,
                                message.start_register, message.end_register, result, message.data), rest[1:]


@dataclass(init=False)
class MultiRegisterValueMessage(MultiRegisterMessage):
    """A message that specifies multiple registers and values."""
    values: list[int]

    def __init__(self, protocol: int, device_id: int, record_type: int,
                 datalogger_id: bytes, start_register: int, end_register: int, values: list[int], raw: bytes = None):
        """
        :param values: The values read from or to write to the registers.
        """
        super().__init__(protocol, device_id, record_type, datalogger_id, start_register, end_register, raw)
        self.values = values

    @property
    def body(self) -> bytes:
        if self._body is not None:
            return self._body
        self._body = super().body
        self._body += b"".join([value.to_bytes(2, "big") for value in self.values])
        return self._body

    @classmethod
    def deserialize(cls, raw: bytes) -> (MultiRegisterValueMessage, bytes):
        message, rest = super().deserialize(raw)
        number_of_values = message.end_register - message.start_register + 1
        if len(rest) < number_of_values * 2:
            raise ValueError(f"Expected {number_of_values} values, got {rest}")
        try:
            values = [int.from_bytes(rest[i * 2:(i + 1) * 2], "big") for i in
                      range(number_of_values)]
        except IndexError or ValueError:
            raise ValueError(f"Expected values in content, got {message.content}")
        return MultiRegisterValueMessage(message.protocol, message.device_id, message.record_type,
                                         message.datalogger_id, message.start_register, message.end_register, values,
                                         raw), rest[number_of_values * 2:]
