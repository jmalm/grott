from __future__ import annotations

from dataclasses import dataclass

from .message import MessageWithRecordType
from .single_register_messages import SingleRegisterAck


@dataclass(init=False)
class DataloggerPutAck(SingleRegisterAck, MessageWithRecordType):
    RECORD_TYPE = 24  # 0x18

    @classmethod
    def deserialize(cls, raw: bytes) -> (DataloggerPutAck, bytes):
        message, rest = super().deserialize(raw)
        if rest:
            raise ValueError(f"Expected no remaining bytes, got {rest}")
        return DataloggerPutAck(message.protocol, message.device_id, cls.RECORD_TYPE, message.datalogger_id,
                                message.register, message.result, raw), rest
