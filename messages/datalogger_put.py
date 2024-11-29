from messages.response import Response


class DataloggerPutResponse(Response):
    record_type = 24  # 0x18

    def __init__(self, data):
        super().__init__(data)
        self.result = self.data[40:42]
        self.response = {"result": self.result}
