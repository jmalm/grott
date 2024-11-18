from messages.datalogger_get import DataloggerGetResponse
from messages.datalogger_put import DataloggerPutResponse
from messages.inverter_get import InverterGetResponse
from messages.inverter_put import InverterPutResponse, InverterPutMultipleResponse
from messages.logger_message import LoggerMessage


def get_logger_message(data):
    message = LoggerMessage(data)
    for cls in response_classes:
        if message.record_type == cls.record_type:
            return cls(data)
    return message


response_classes = [
    InverterGetResponse,
    InverterPutResponse,
    DataloggerGetResponse,
    DataloggerPutResponse,
    InverterPutMultipleResponse,
]
