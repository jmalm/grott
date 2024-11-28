from grottdata import decrypt
from messages.datalogger_get import DataloggerGetResponse
from messages.datalogger_put import DataloggerPutResponse
from messages.inverter_get import InverterGetResponse
from messages.inverter_put import InverterPutResponse, InverterPutMultipleResponse, InverterPutMultipleCommand
from messages.logger_message import LoggerMessage


def get_logger_message(data):
    message = LoggerMessage(data)
    for cls in response_classes:
        if message.record_type == cls.record_type:
            return cls(data)
    return message


def deserialize(raw):
    message = {"raw": raw}
    try:
        message["header"] = raw[:8]  # First 8 bytes is the header.
        message["send_sequence"] = get_word(message["header"], 0)
        message["protocol"] = get_word(message["header"], 1)
        message["body_length"] = get_word(message["header"], 2)
        message["device_id"] = message["header"][6]
        message["send_command"] = message["header"][7]

        message["decrypted"] = decrypt(raw, return_bytes=True)  # TODO: Check datalogger if it uses encryption.
        message["datalogger_id"] = message["decrypted"][8:18]  # I don't know if this is part of all messages.

        buffer_length_in_bytes = 20 if message["protocol"] == 6 else 0
        message["body"] = message["decrypted"][18 + buffer_length_in_bytes:]

        message["multiregister"] = message["send_command"] == 16

        message["start_register"] = get_word(message["body"], 0)
        message["end_register"] = get_word(message["body"], 1) if message["multiregister"] else message["start_register"]
        message["registers"] = list(range(message["start_register"], message["end_register"] + 1))

        data_start = 2 if message["multiregister"] else 1
        data_stop = data_start + len(message["registers"])
        message["values"] = [get_word(message["body"], position) for position in range(data_start, data_stop)]

        if message["send_command"] == 16:
            print(message)
            return InverterPutMultipleCommand(**message)

        # TODO: Handle other messages. At least, return a Message, not a dict.
        return message
    except:
        print(message)
        raise



def get_word(decrypted: bytes, word_position: int):
    byte_position = word_position * 2
    return int.from_bytes(decrypted[byte_position:byte_position + 2], byteorder="big")


response_classes = [
    InverterGetResponse,
    InverterPutResponse,
    DataloggerGetResponse,
    DataloggerPutResponse,
    InverterPutMultipleResponse,
]
