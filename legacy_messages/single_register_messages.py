from __future__ import annotations

from dataclasses import dataclass

from messages.ack import Ack
from messages.data_message import DataMessage


@dataclass(init=False)
class SingleRegisterMessage(DataMessage):
    """A message that specifies a single register."""
    register: int

    def __init__(self, protocol: int, device_id: int, record_type: int,
                 datalogger_id: bytes, register: int, raw: bytes = None):
        """
        :param register: The register to read / write.
        """
        super().__init__(protocol, device_id, record_type, datalogger_id, raw)
        self.register = register

    @property
    def body(self) -> bytes:
        return (super().body +
                self.register.to_bytes(2, "big"))

    @classmethod
    def deserialize(cls, raw: bytes) -> (SingleRegisterMessage, bytes):
        message, rest = super().deserialize(raw)
        if len(rest) < 2:
            raise ValueError(f"Expected register, got {rest}")
        try:
            register = int.from_bytes(rest[0:2], "big")
        except ValueError:
            raise ValueError(f"Expected register in first word of content, got {rest}")
        return SingleRegisterMessage(message.protocol, message.device_id, message.record_type, message.datalogger_id, register, raw), rest[2:]


@dataclass(init=False)
class SingleRegisterAck(SingleRegisterMessage, Ack):
    value: int

    def __init__(self, protocol: int, device_id: int, record_type: int, datalogger_id: bytes, register: int,
                 result: int, value: int, raw: bytes = None):
        super().__init__(protocol, device_id, record_type, datalogger_id, register, raw)
        self.result = result
        self.value = value

    @property
    def body(self) -> bytes:
        return (super().body +
                self.result.to_bytes(1, "big") +
                self.value.to_bytes(2, "big"))

    @classmethod
    def deserialize(cls, raw: bytes) -> (SingleRegisterAck, bytes):
        message, rest = super().deserialize(raw)
        if len(rest) < 3:
            raise ValueError(f"Expected ack result and value, got {rest}")
        result = int(rest[0])
        value = int.from_bytes(rest[1:3], "big")
        return SingleRegisterAck(message.protocol, message.device_id, message.record_type, message.datalogger_id,
                                 message.register, result, value, message.data), rest[3:]


@dataclass(init=False)
class SingleRegisterValueMessage(SingleRegisterMessage):
    """A message that specifies a single register and a value."""
    value: int

    def __init__(self, protocol: int, device_id: int, record_type: int,
                 datalogger_id: bytes, register: int, value: int, raw: bytes = None):
        """
        :param value: The value read from or to write to the register.
        """
        super().__init__(protocol, device_id, record_type, datalogger_id, register, raw)
        self.value = value

    @property
    def body(self) -> bytes:
        return (super().body +
                self.value.to_bytes(2, "big"))

    @classmethod
    def deserialize(cls, raw: bytes) -> (SingleRegisterValueMessage, bytes):
        message, rest = super().deserialize(raw)
        if len(rest) < 2:
            raise ValueError(f"Expected value, got {rest}")
        try:
            value = int.from_bytes(rest[0:2], "big")
        except IndexError or ValueError:
            raise ValueError(f"Expected value in third word of content, got {message.content}")
        return SingleRegisterValueMessage(message.protocol, message.device_id, message.record_type, message.datalogger_id,
                   message.register, value, raw), rest[2:]


