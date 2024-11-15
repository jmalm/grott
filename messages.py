import codecs

from grottdata import decrypt


def get(data, position: int, length: int):
    return data[position:position + length]


def get_message(data):
    message = Message(data)
    for cls in command_response_classes:
        if message.record_type == cls.record_type:
            return cls(data)
    return message


class Message:
    is_encrypted_ack = False
    offset = 0

    def __init__(self, raw):
        self.raw = raw
        self.header = "".join("{:02x}".format(n) for n in self.raw[0:8])
        self.sequence_number = self.header[0:4]
        self.protocol = self.header[6:8]
        self.inverter_no = self.header[12:14]
        self.record_type = self.header[14:16]

        self.offset = 40 if self.protocol == "06" else 0

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


class CommandResponse(Message):
    response = {}


class InverterGetResponse(CommandResponse):
    record_type = "05"
    is_encrypted_ack = True

    def __init__(self, data):
        super().__init__(data)
        self.value = self.get_data(44, 4) if len(self.data) != 48 else None
        self.response = {"value": self.value}


class InverterPutResponse(CommandResponse):
    record_type = "06"
    is_encrypted_ack = True
    offset = 40

    def __init__(self, data):
        super().__init__(data)
        self.result = self.get_data(40, 2)
        self.value = self.get_data(42, 4)
        self.response = {"value": self.value, "result": self.result}


class DataloggerGetResponse(CommandResponse):
    record_type = "19"

    def __init__(self, data):
        super().__init__(data)
        value_length = int(self.data[40:44], base=16)
        self.value = codecs.decode(self.data[44:44 + value_length * 2], "hex")
        self.response = {"value": self.value}


class DataloggerPutResponse(CommandResponse):
    record_type = "18"

    def __init__(self, data):
        super().__init__(data)
        self.result = self.data[40:42]
        self.response = {"result": self.result}


class InverterPutMultipleResponse(CommandResponse):
    record_type = "10"

    def __init__(self, data):
        super().__init__(data)
        self.value = self.data[84:86]  # TODO: why only two bytes?
        self.response = {"value": self.value}

    def register_key(self):
        start_register = int(self.data[76:80], base=16)
        end_register = int(self.data[80:84], base=16)
        return f"{start_register:04x}{end_register:04x}"


command_response_classes = [
    InverterGetResponse,
    InverterPutResponse,
    DataloggerGetResponse,
    DataloggerPutResponse,
    InverterPutMultipleResponse,
]
