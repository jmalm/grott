from __future__ import annotations

import codecs

from messages.response import Response


class DataloggerGetResponse(Response):
    record_type = "19"

    def __init__(self, data):
        super().__init__(data)
        value_length = int(self.data[40:44], base=16)
        self.value = codecs.decode(self.data[44:44 + value_length * 2], "hex")
        self.response = {"value": self.value}
