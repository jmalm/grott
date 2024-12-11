import datetime
import json
import os
from dataclasses import dataclass, field

import messages
from util import get_record_type, get_decrypted


class MessageCollectorFull(Exception):
    def __init__(self, max_messages: int = 0):
        super().__init__(f"Max messages reached ({max_messages})")


@dataclass
class CollectedMessage:
    raw: bytes
    address: str
    port: int
    datetime: datetime.datetime
    from_datalogger: bool
    message: messages.Message = field(default=None, init=False)

    def __post_init__(self):
        message_classes = messages.from_datalogger if self.from_datalogger else messages.to_datalogger
        self.message = messages.deserialize(get_decrypted(self.raw), message_classes)

    def to_dict(self) -> dict:
        return dict(
            message=self.message.to_dict(),
            datetime=self.datetime.isoformat(),
            address=self.address,
            port=self.port,
            from_datalogger=self.from_datalogger,
            raw=self.raw.hex()
        )


class MessageCollector:
    """
    A class to collect messages.
    """
    def __init__(self, max_messages: int = 0):
        self.max_messages = max_messages
        self.messages: list[CollectedMessage] = []

    def add(self, raw: bytes, address: str, port: int, from_datalogger: bool):
        if len(self.messages) >= self.max_messages:
            raise MessageCollectorFull(self.max_messages)
        self.messages.append(CollectedMessage(raw, address, port, datetime.datetime.now(), from_datalogger))

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

    def to_json(self) -> str:
        """
        Return the collected messages as a JSON string.
        """
        return json.dumps([m.to_dict() for m in self.messages])
