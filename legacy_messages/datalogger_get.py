from __future__ import annotations

from dataclasses import dataclass

from .message import MessageWithRecordType
from .command import Command
from .multi_register_messages import MultiRegisterMessage, MultiRegisterValueMessage
from .single_register_messages import SingleRegisterValueMessage


@dataclass(init=False)
class DataloggerGetCommand(MultiRegisterMessage, MessageWithRecordType, Command):
    RECORD_TYPE = 25  # 0x19
    device_id = "01"  # Always 1 for datalogger
    response_format: str = "dec"

    def __init__(self, protocol: int, device_id: int, datalogger_id: bytes, start_register: int, end_register: int,
                 response_format: str = "dec", raw: bytes = None):
        super().__init__(protocol, device_id, self.RECORD_TYPE, datalogger_id, start_register, end_register, raw)
        self.response_format = response_format

    @classmethod
    def deserialize(cls, raw) -> (DataloggerGetCommand, bytes):
        message, rest = super().deserialize(raw)
        if rest:
            raise ValueError(f"Expected no remaining bytes, got {rest}")
        return DataloggerGetCommand(message.protocol, message.device_id, message.datalogger_id, message.start_register,
                                    message.end_register, raw=raw), rest


@dataclass(init=False)
class DataloggerGetResponse(MultiRegisterValueMessage, MessageWithRecordType):
    RECORD_TYPE = DataloggerGetCommand.RECORD_TYPE

    def __init__(self, protocol: int, device_id: int, record_type: int, datalogger_id: bytes,
                 start_register: int, end_register: int, values: list[int], raw: bytes = None):
        super().__init__(protocol, device_id, record_type, datalogger_id, start_register, end_register, values, raw)
        self.response = {"value": self.values}

    @classmethod
    def deserialize(cls, raw) -> (DataloggerGetResponse, bytes):
        message, rest = super().deserialize(raw)
        expected_number_of_values = message.end_register - message.start_register + 1
        try:
            value_length = int.from_bytes(message.data[20:22], byteorder="big")
            if value_length != expected_number_of_values:
                raise ValueError(f"Expected value length {expected_number_of_values}, got {value_length}")
            values = [int.from_bytes(rest[i * 2:(i + 1) * 2], "big") for i in
                      range(value_length)]
        except ValueError:
            raise ValueError(f"Could not decode values: {rest}")
        return DataloggerGetResponse(message.protocol, message.device_id, message.record_type, message.datalogger_id,
                                     message.start_register, message.end_register, values, message.data), rest[2:]
