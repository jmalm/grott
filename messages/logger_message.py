import codecs

from grottdata import decrypt
from .message import Message


class LoggerMessage(Message):
    """A message sent from the datalogger, possibly as a response to a command sent to it."""

    def __init__(self, raw):
        self.raw = raw
        self.header = "".join("{:02x}".format(n) for n in self.raw[0:8])
        self.sequence_number = self.header[0:4]
        self.protocol = self.header[6:8]
        self.inverter_no = self.header[12:14]
        self.record_type = self.header[14:16]

        self.is_data_record = self.record_type in ["03", "04", "50", "1b", "20"]
        self.is_command_response_record = self.record_type in ["19", "05", "06", "18"]

        self._data = None

    @property
    def data(self):
        if self._data is None:
            self._data = decrypt(self.raw) if self.is_encrypted_ack else "".join("{:02x}".format(n) for n in self.raw)
        # TODO: Try alternative implementation: self.data = decrypt(data) if self.is_encrypted_ack else data.hex()
        return self._data

    @property
    def register_key(self):
        register = int(self.get_data(36, 4), base=16)
        return f"{register:04x}"

    @property
    def logger_id(self):
        _id = self.get_data(16, 20)
        return codecs.decode(_id, "hex")

    def get_data(self, base_position: int, length: int):
        position = base_position + self.offset
        return self.data[position:position + length]
