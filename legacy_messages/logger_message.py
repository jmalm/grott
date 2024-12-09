from __future__ import annotations

from .data_message import DataMessage
from .single_register_messages import SingleRegisterMessage


class LoggerMessage(SingleRegisterMessage):  # TODO: Create RegisterMessage that provides register_key. (Maybe not needed?)
    """A message sent from the datalogger, possibly as a response to a command sent to it."""

    def __init__(self, protocol: int, device_id: int, record_type: int, datalogger_id: bytes, register: int, raw: bytes = None):
        super().__init__(protocol, device_id, record_type, datalogger_id, register, raw)

        self.is_data_record = self.record_type in ["03", "04", "50", "1b", "20"]
        self.is_command_response_record = self.record_type in ["19", "05", "06", "18"]

        self._data = None

    @property
    def register_key(self):
        register = int(self.get_data(36, 4), base=16)
        return f"{register:04x}"

    @property
    def logger_id(self) -> bytes:
        return self.datalogger_id

    @property
    def inverter_no(self) -> str:
        return f"{self.device_id:02x}"

    def get_data(self, base_position: int, length: int):
        position = base_position + self.buffer_length * 2  # 2 bytes per hex character
        return self.data[position:position + length]

    @classmethod
    def deserialize(cls, raw) -> LoggerMessage:
        message = super().deserialize(raw)

        return LoggerMessage(message.protocol, message.device_id, message.record_type, message.datalogger_id,
                             message.register, message.data)
