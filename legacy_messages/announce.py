from __future__ import annotations

from dataclasses import dataclass

from .message import MessageWithRecordType
from .data_message import DataMessage


@dataclass(init=False)
class AnnounceMessage(DataMessage, MessageWithRecordType):
    RECORD_TYPE = 3
    inverter_id: str  # TODO: Change to bytes?

    def __init__(self, protocol: int, device_id: int, record_type: int, datalogger_id: bytes,
                 inverter_id: bytes, raw: bytes = None):
        super().__init__(protocol, device_id, record_type, datalogger_id, raw)
        self._inverter_id = inverter_id

    @property
    def logger_id(self):
        return self.datalogger_id.decode("utf-8")

    @property
    def inverter_id(self):
        return self._inverter_id.decode("utf-8")

    @classmethod
    def deserialize(cls, raw) -> (AnnounceMessage, bytes):
        message, rest = super().deserialize(raw)
        if len(rest) < 10:  # TODO: Seems like messages with record type 3 don't always have a body. Maybe it's a command from the server for the datalogger to send an announce message?
            raise ValueError(f"Could not decode inverter id: {rest}")
        inverter_id = rest[:10]
        return AnnounceMessage(message.protocol, message.device_id, message.record_type, message.datalogger_id,
                               inverter_id, message.data), rest[10:]
