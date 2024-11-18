from messages.response import Response


class InverterPutResponse(Response):
    record_type = "06"
    is_encrypted_ack = True
    offset = 40

    def __init__(self, data):
        super().__init__(data)
        self.result = self.get_data(40, 2)
        self.value = self.get_data(42, 4)
        self.response = {"value": self.value, "result": self.result}


class InverterPutMultipleResponse(Response):
    record_type = "10"

    def __init__(self, data):
        super().__init__(data)
        self.value = self.data[84:86]  # TODO: why only two bytes?
        self.response = {"value": self.value}

    def register_key(self):
        start_register = int(self.data[76:80], base=16)
        end_register = int(self.data[80:84], base=16)
        return f"{start_register:04x}{end_register:04x}"
