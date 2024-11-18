from __future__ import annotations


class Message:
    """A message that can be either to or from the datalogger."""
    is_encrypted_ack = False
    raw: bytes
    header: str
    protocol: str
    record_type: str
    protocol: str | None = None

    @property
    def offset(self):
        return 40 if self.protocol == "06" else 0
