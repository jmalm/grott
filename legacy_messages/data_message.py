from __future__ import annotations

from dataclasses import dataclass

from messages.message import Message


@dataclass(init=False)
class DataMessage(Message):
    """A message that contains data."""
    datalogger_id: bytes

    def __init__(self, protocol: int, device_id: int, record_type: int,
                 datalogger_id: bytes,
                 raw: bytes = None):
        super().__init__(protocol, device_id, record_type, raw)
        self._datalogger_id = datalogger_id

    @property
    def datalogger_id(self) -> bytes:
        """The datalogger id."""
        return self._datalogger_id

    @property
    def body(self) -> bytes:
        if self._body is not None:
            return self._body
        self._body = super().body
        self._body += self.datalogger_id
        self._body += self.buffer
        return self._body

    @property
    def buffer_length(self) -> int:
        """The number of bytes between datalogger id and content."""
        return 20 if self.protocol == 6 else 0

    @property
    def buffer(self) -> bytes:
        """The buffer between datalogger id and content."""
        return int(0).to_bytes(1, byteorder="big") * self.buffer_length

    @property
    def content(self) -> bytes:
        """
        The content of the message.
        TODO: content, body, data, raw... this is confusing. Is all of it necessary to expose?
        """
        datalogger_id_length = 10
        content_position = datalogger_id_length + self.buffer_length
        return self.body[content_position:]

    @classmethod
    def deserialize(cls, raw: bytes) -> (DataMessage, bytes):
        message, rest = super().deserialize(raw)
        if len(rest) < 10:
            raise ValueError(f"Expected datalogger id in first 10 bytes, got {rest}")
        datalogger_id = rest[0:10]

        message = DataMessage(message.protocol, message.device_id, message.record_type, datalogger_id, raw)
        return message, rest[10 + message.buffer_length:]
