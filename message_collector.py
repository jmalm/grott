import datetime
import json
import os

from util import get_record_type


class MessageCollectorFull(Exception):
    def __init__(self, max_messages: int = 0):
        super().__init__(f"Max messages reached ({max_messages})")


class MessageCollector:
    """
    A class to collect messages.
    """
    def __init__(self, max_messages: int = 0):
        self.max_messages = max_messages
        self.messages: list[dict] = []

    def add(self, data: bytes, address: str, port: int):
        if len(self.messages) >= self.max_messages:
            raise MessageCollectorFull(self.max_messages)
        self.messages.append(dict(data=data, address=address, port=port, datetime=datetime.datetime.now().isoformat()))

    def store(self, path: str = "collected_messages", filename_template: str = "{datetime}--{address}-{port}--{record_type}.bin"):
        """Store the collected messages in separate files in the given path."""
        if not os.path.exists(path):
            os.makedirs(path)
        for message in self.messages:
            dt = datetime.datetime.now()
            record_type = get_record_type(message["data"])
            filename = filename_template.format(datetime=dt, record_type=record_type, address=message["address"], port=message["port"])
            with open(os.path.join(path, filename), "wb") as f:
                f.write(message["data"])

    def to_json(self):
        """
        Return the collected messages as a JSON string.

        Converts the bytes message to hex string to be compatible with JSON.
        """
        messages = []
        for message in self.messages:
            message = dict(**message)  # Create a copy
            message["data"] = message["data"].hex()  # Convert the raw data to string of hex digits (two per byte) TODO: return parsed message too
            messages.append(message)
        return json.dumps(messages)
