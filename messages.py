from dataclasses import dataclass, InitVar, field


@dataclass(kw_only=True)
class Message:
    """A message that can be either to or from the datalogger or inverter."""
    send_sequence: int = None
    protocol: int = None
    device_id: int = None
    record_type: int = None
    data: InitVar[bytes] = None
    _body_length: int = field(default=None, init=False, repr=False)

    def __post_init__(self, data: bytes):
        if data is None:
            return
        _ = self.deserialize(data)

    def deserialize(self, data: bytes) -> bytes:
        try:
            header = data[0:8]
        except IndexError:
            raise ValueError(f"Expected at least 8 bytes, got {data}")
        try:
            self.send_sequence = int.from_bytes(header[:2], "big")
        except ValueError:
            raise ValueError(f"Expected send sequence in word 0 of header, got header: {header}")
        try:
            self.protocol = int.from_bytes(header[2:4], "big")
        except ValueError:
            raise ValueError(f"Expected protocol in word 1 of header, got header: {header}")
        try:
            self._body_length = int.from_bytes(header[4:6], "big")
        except ValueError:
            raise ValueError(f"Expected body length in word 2 of header, got header: {header}")
        self.device_id = data[6]
        self.record_type = data[7]

        return data[8:]

    @property
    def buffer_length(self) -> int:
        """The number of bytes between datalogger id and content."""
        return 20 if self.protocol == 6 else 0

    @property
    def header(self) -> bytes:
        """The first 8 bytes of the message. Never encrypted."""
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
        return b""

    def serialize(self) -> bytes:
        return self.header + self.body


@dataclass(kw_only=True)
class Ack:
    """Ack messages are returned by the datalogger or inverter on put requests."""
    result: int = None


@dataclass(kw_only=True)
class DataMessage(Message):
    """Message that contains data."""
    datalogger_id: bytes = None
    
    def deserialize(self, data: bytes) -> bytes:
        rest = super().deserialize(data)
        if len(rest) < 10:
            raise ValueError(f"Expected datalogger id in first 10 bytes, got {rest}")
        self.datalogger_id = rest[0:10]
        return rest[10 + self.buffer_length:]

    @property
    def body(self) -> bytes:
        return (super().body +
                self.datalogger_id +
                b"\x00" * self.buffer_length)


@dataclass(kw_only=True)
class SingleRegisterMessage(DataMessage):
    """Message that specifies a single register."""
    register: int = None

    def deserialize(self, data: bytes) -> bytes:
        rest = super().deserialize(data)
        if len(rest) < 2:
            raise ValueError(f"Expected register, got {rest}")
        self.register = int.from_bytes(rest[:2], "big")
        return rest[2:]

    @property
    def body(self) -> bytes:
        return (super().body +
                self.register.to_bytes(2, "big"))


@dataclass(kw_only=True)
class SingleRegisterValueMessage(SingleRegisterMessage):
    """Message that specifies a single register and its value."""
    value: int = None
    
    def deserialize(self, data: bytes) -> bytes:
        rest = super().deserialize(data)
        if len(rest) < 2:
            raise ValueError(f"Expected value, got {rest}")
        self.value = int.from_bytes(rest[:2], "big")
        return rest[2:]

    @property
    def body(self) -> bytes:
        return (super().body +
                self.value.to_bytes(2, "big"))


@dataclass(kw_only=True)
class SingleRegisterAck(SingleRegisterMessage, Ack):
    value: int = None

    def deserialize(self, data: bytes) -> bytes:
        rest = super().deserialize(data)
        if len(rest) < 3:
            raise ValueError(f"Expected ack result and value, got {rest}")
        self.result = int(rest[0])
        self.value = int.from_bytes(rest[1:3], "big")
        return rest[3:]

    @property
    def body(self) -> bytes:
        return (super().body +
                self.result.to_bytes(1, "big") +
                self.value.to_bytes(2, "big"))


@dataclass
class MultiRegisterMessage(DataMessage):
    start_register: int = None
    end_register: int = None

    def deserialize(self, data: bytes) -> bytes:
        rest = super().deserialize(data)
        if len(rest) < 4:
            raise ValueError(f"Expected start and end registers, got {rest}")
        self.start_register = int.from_bytes(rest[:2], "big")
        self.end_register = int.from_bytes(rest[2:4], "big")
        return rest[4:]


@dataclass
class MultiRegisterValueMessage(MultiRegisterMessage):
    values: list[int] = None

    def deserialize(self, data: bytes) -> bytes:
        rest = super().deserialize(data)
        num_values = (self.end_register - self.start_register + 1)
        if len(rest) < 2 * num_values:
            raise ValueError(f"Expected {num_values} values, got {rest}")
        self.values = [int.from_bytes(rest[i:i+2], "big") for i in range(0, num_values * 2, 2)]
        return rest[2 * num_values:]


@dataclass
class MultiRegisterAck(MultiRegisterMessage, Ack):
    def deserialize(self, data: bytes) -> bytes:
        rest = super().deserialize(data)
        if len(rest) < 1:
            raise ValueError(f"Expected ack result, got {rest}")
        self.result = int(rest[0])
        return rest[1:]


def final(cls):
    """Asserts that there is no data left after deserialization."""
    original_deserialize = cls.deserialize

    def wrapped_deserialize(self, data: bytes) -> bytes:
        rest = original_deserialize(self, data)
        if rest != b"":
            raise AssertionError(f"Expected {self}.deserialize() to return empty, got: {rest}")
        return rest

    cls.deserialize = wrapped_deserialize
    return cls


@dataclass(kw_only=True)
@final
class InverterGetSingle(SingleRegisterMessage):
    record_type = None  # Don't know what this is


@dataclass(kw_only=True)
@final
class InverterGetSingleResponse(SingleRegisterValueMessage):
    record_type = InverterGetSingle.record_type


@dataclass(kw_only=True)
@final
class InverterPutSingle(SingleRegisterValueMessage):
    record_type = 6


@dataclass(kw_only=True)
@final
class InverterPutSingleAck(SingleRegisterAck):
    record_type: int = InverterPutSingle.record_type


@dataclass(kw_only=True)
@final
class InverterGetMulti(MultiRegisterMessage):
    record_type = 5  # I _think_ this is correct


@dataclass(kw_only=True)
@final
class InverterGetMultiResponse(MultiRegisterValueMessage):
    record_type = InverterGetMulti.record_type


@dataclass(kw_only=True)
@final
class InverterPutMulti(MultiRegisterValueMessage):
    record_type = 16


@dataclass(kw_only=True)
@final
class InverterPutMultiAck(MultiRegisterAck):
    record_type = InverterPutMulti.record_type


@dataclass(kw_only=True)
@final
class Announcement(DataMessage):
    record_type = 3
    inverter_id: bytes = None

    def deserialize(self, data: bytes) -> bytes:
        rest = super().deserialize(data)
        if len(rest) < 10:
            raise ValueError(f"Expected inverter id, got {rest}")
        self.inverter_id = rest[:10]
        return rest[10:]


@dataclass(kw_only=True)
@final
class DataloggerGetMulti(MultiRegisterMessage):
    record_type = 25
    device_id = 1  # Always 1 for datalogger (?)


@dataclass(kw_only=True)
@final
class DataloggerGetMultiResponse(MultiRegisterValueMessage):
    record_type = DataloggerGetMulti.record_type
    device_id = DataloggerGetMulti.device_id


@dataclass(kw_only=True)
@final
class DataloggerPutSingleAck(SingleRegisterAck):
    record_type = 24
    device_id = 1


# Messages that can be sent to the datalogger
to_datalogger = [
    InverterGetSingle,
    InverterPutSingle,
    InverterGetMulti,
    InverterPutMulti,
    DataloggerGetMulti,  # TODO: some messages missing...
]


# Messages that can be received from the datalogger
from_datalogger = [
    InverterGetSingleResponse,
    InverterPutSingleAck,
    InverterGetMultiResponse,
    InverterPutMultiAck,
    DataloggerGetMultiResponse,
    DataloggerPutSingleAck,  # TODO: some messages missing...
]
