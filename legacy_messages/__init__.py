from .announce import AnnounceMessage
from .datalogger_get import DataloggerGetResponse, DataloggerGetCommand
from .datalogger_put import DataloggerPutAck
from .inverter_get import InverterGetResponse
from .inverter_put import InverterPutSingle, InverterPutMultiple, InverterPutMultipleAck, InverterPutSingleAck
from .logger_message import LoggerMessage
from .message import Message, MessageWithRecordType
from .util import get_word


message_classes_from_server: list[type[MessageWithRecordType]] = []
message_classes_from_datalogger: list[type[MessageWithRecordType]] = []


def add_message_class(cls: type[MessageWithRecordType], message_classes: list[type[MessageWithRecordType]]):
    assert cls.RECORD_TYPE is not None
    message_classes.append(cls)


add_message_class(InverterPutSingle, message_classes_from_server)
add_message_class(InverterPutMultiple, message_classes_from_server)
# add_message_class(DataloggerGetCommand, message_classes_from_server)  # Don't care about datalogger commands at the moment. They seem to be encoded differently.

add_message_class(AnnounceMessage, message_classes_from_datalogger)
add_message_class(InverterGetResponse, message_classes_from_datalogger)
add_message_class(InverterPutSingleAck, message_classes_from_datalogger)
add_message_class(InverterPutMultipleAck, message_classes_from_datalogger)
# add_message_class(DataloggerGetResponse, message_classes_from_datalogger)
# add_message_class(DataloggerPutAck, message_classes_from_datalogger)


def deserialize(raw: bytes, message_classes: list[type(MessageWithRecordType)] = None) -> (Message, bytes):
    """Returns a message and the remaining bytes in the buffer."""
    if message_classes is None:
        message_classes = message_classes_from_server + message_classes_from_datalogger
    try:
        record_type = raw[7]
    except IndexError:
        raise ValueError(f"Expected record type in byte 7 of header, got header: {raw[:8]}")
    for cls in message_classes:
        if record_type == cls.RECORD_TYPE:
            return cls.deserialize(raw)
    return Message.deserialize(raw)
