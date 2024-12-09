from __future__ import annotations

from dataclasses import dataclass

from messages.single_register_messages import SingleRegisterValueMessage, SingleRegisterAck
from messages.multi_register_messages import MultiRegisterValueMessage, MultiRegisterAck
from messages.message import MessageWithRecordType


@dataclass(init=False)
class InverterPutSingle(SingleRegisterValueMessage, MessageWithRecordType):
    RECORD_TYPE = 6

    @classmethod
    def deserialize(cls, raw: bytes) -> (InverterPutSingle, bytes):
        message, rest = super().deserialize(raw)
        if rest:
            raise ValueError(f"Expected no remaining bytes, got {rest}")
        return InverterPutSingle(message.protocol, message.device_id, cls.RECORD_TYPE, message.datalogger_id,
                                 message.register, message.value, raw), rest


# Det verkar som att InverterPutAck har startregister, endregister (kan vara 0000), antal värden. # TODO: Check this out!

@dataclass(init=False)
class InverterPutSingleAck(SingleRegisterAck, MessageWithRecordType):
    RECORD_TYPE = InverterPutSingle.RECORD_TYPE  # 0x06

    @classmethod
    def deserialize(cls, raw: bytes) -> (InverterPutSingleAck, bytes):
        message, rest = super().deserialize(raw)
        if len(rest):
            raise ValueError(f"Expected no remaining bytes, got {rest}")
        return InverterPutSingleAck(message.protocol, message.device_id, cls.RECORD_TYPE, message.datalogger_id,
                                    message.register, message.result, message.value, raw), rest


@dataclass(init=False)
class InverterPutMultiple(MultiRegisterValueMessage, MessageWithRecordType):
    RECORD_TYPE = 16  # 0x10

    @classmethod
    def deserialize(cls, raw: bytes) -> (InverterPutMultiple, bytes):
        message, rest = super().deserialize(raw)
        if rest:
            raise ValueError(f"Expected no remaining bytes, got {rest}")
        return InverterPutMultiple(message.protocol, message.device_id, cls.RECORD_TYPE, message.datalogger_id,
                                   message.start_register, message.end_register, message.values, raw), rest


@dataclass(init=False)
class InverterPutMultipleAck(MultiRegisterAck, MessageWithRecordType):
    RECORD_TYPE = InverterPutMultiple.RECORD_TYPE  # 0x10

    @classmethod
    def deserialize(cls, raw: bytes) -> (InverterPutMultipleAck, bytes):
        message, rest = super().deserialize(raw)
        if len(rest):
            raise ValueError(f"Expected no remaining bytes, got {rest}")
        return InverterPutMultipleAck(message.protocol, message.device_id, cls.RECORD_TYPE, message.datalogger_id,
                                      message.start_register, message.end_register, message.result, raw), rest
