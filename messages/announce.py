import codecs

from .logger_message import LoggerMessage


class AnnounceMessage(LoggerMessage):
    record_type = "03"

    def __init__(self, data):
        super().__init__(data)

    @property
    def logger_id(self):
        return codecs.decode(self.data[16:36], "hex").decode('utf-8')  # TODO: Why without the offset?

    @property
    def inverter_id(self):
        return codecs.decode(self.get_data(36, 20), "hex").decode('utf-8')

