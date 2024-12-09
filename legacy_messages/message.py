from __future__ import annotations

from dataclasses import dataclass

import libscrc_fake as libscrc

from grottdata import encrypt, decrypt
from messages.util import get_word


@dataclass(init=False)
class Message:
    """A message that can be either to or from the datalogger."""
    is_encrypted_ack = False
    protocol: int
    device_id: int
    record_type: int

    def __init__(self, protocol: int, device_id: int, record_type: int, raw: bytes = None):
        """
        :param protocol: The protocol version.
        """
        self._protocol = protocol
        self._device_id = device_id
        self._record_type = record_type
        self._body = None
        self._raw = raw  # TODO: Use this to get the raw message in self.raw?

    @property
    def protocol(self) -> int:
        """
        The protocol version.
        Decides how to encode / decode the message (buffer, encryption)
        """
        return self._protocol

    @property
    def device_id(self) -> int:
        """What is this?!?"""
        return self._device_id

    @property
    def record_type(self) -> int:
        """The type of message."""
        return self._record_type

    @property
    def header(self) -> bytes:
        """The first 8 bytes of the message. Never (?) encrypted."""
        send_sequence = 1  # Not sure what this means
        body_length_with_crc = len(self.body) + 2
        return (send_sequence.to_bytes(2, "big") +
                self.protocol.to_bytes(2, "big") +
                body_length_with_crc.to_bytes(2, "big") +
                self.device_id.to_bytes(1, "big") +
                self.record_type.to_bytes(1, "big"))

    @property
    def body(self) -> bytes:
        """The information-carrying part of the message."""
        if self._body is not None:
            return self._body
        self._body = b""
        return self._body

    @property
    def data(self) -> bytes:
        """TODO: Remove this. Should be the same as *decrypted*."""
        return self.header + self.body

    @property
    def raw(self) -> bytes:
        """TODO: Remove this. Just use *serialize()*."""
        if self.protocol == 2:
            return self.data

        encrypted = encrypt(self.data, return_bytes=True)
        crc16 = libscrc.modbus(encrypted)
        return encrypted + crc16.to_bytes(2, "big")

    def serialize(self):
        """Serialize a message to bytes. Encrypted if the protocol demands it."""
        return self.raw

    def __repr__(self):
        return f"{self.__class__.__name__}(protocol={self.protocol}, device_id={self.device_id}, " \
               f"record_type={self.record_type})"

    @classmethod
    def deserialize(cls, raw: bytes) -> (Message, bytes):
        """
        Deserialize a message from bytes.
        :param raw: The raw message bytes.
        :return: The message and the rest of the (decrypted) bytes, with the crc stripped.
        """
        try:
            header = raw[0:8]
        except IndexError:
            raise ValueError(f"Expected at least 8 bytes, got {raw}")
        try:
            send_sequence = get_word(header, 0)
        except ValueError:
            raise ValueError(f"Expected send sequence in word 0 of header, got header: {header}")
        try:
            protocol = get_word(header, 1)
        except ValueError:
            raise ValueError(f"Expected protocol in word 1 of header, got header: {header}")
        try:
            body_length = get_word(header, 2)
        except ValueError:
            raise ValueError(f"Expected body length in word 2 of header, got header: {header}")
        device_id = raw[6]
        record_type = raw[7]

        decrypted = raw
        if protocol != 2:  # Protocol 2 is not encrypted
            decrypted = decrypt(raw, return_bytes=True)[:-2]  # Decrypt, and strip crc

        message = Message(protocol, device_id, record_type, raw)
        return message, decrypted[8:]


@dataclass(frozen=True)
class Header:
    send_sequence: int
    protocol: int
    body_length: int
    device_id: int
    record_type: int
    raw: bytes  # = None

    # def __init__(self, send_sequence: int, protocol: int, body_length: int, device_id: int, record_type: int, raw: bytes = None):
    #     super().__init__(protocol, device_id, record_type, raw)
    #     self.send_sequence = send_sequence
    #     self.body_length = body_length

    # def __repr__(self):
    #     return f"{self.__class__.__name__}(send_sequence={self.send_sequence}, protocol={self.protocol}, " \
    #            f"body_length={self.body_length}, device_id={self.device_id}, record_type={self.record_type})"

    @classmethod
    def deserialize(cls, raw: bytes) -> (Header, bytes):
        message, rest = Message.deserialize(raw)
        send_sequence = get_word(raw, 0)
        body_length = get_word(raw, 2)
        return Header(send_sequence, message.protocol, body_length, message.device_id, message.record_type, raw), rest


class MessageWithRecordType(Message):
    RECORD_TYPE: int
