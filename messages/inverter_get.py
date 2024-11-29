from messages.response import Response


class InverterGetResponse(Response):
    record_type = 5
    is_encrypted_ack = True

    def __init__(self, data):
        super().__init__(data)
        self.value = self.get_data(44, 4) if len(self.data) != 48 else None
        self.response = {"value": self.value}
