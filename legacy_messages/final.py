def final(cls):
    original_deserialize = cls.deserialize

    def wrapped_deserialize(self, data: bytes) -> bytes:
        result = original_deserialize(self, data)
        if result != b"":
            raise AssertionError(f"{cls.__name__}.deserialize() must return an empty bytes object, got: {result}")
        return result

    cls.deserialize = wrapped_deserialize
    return cls



class A:
    record_type: int = None
    protocol: int = None

    def __init__(self, data):
        self.foo(data)

    def foo(self, data: bytes) -> bytes:
        self.protocol = data[2]
        return data[8:]


class B(A):
    datalogger_id: bytes = None

    def foo(self, data: bytes) -> bytes:
        rest = super().foo(data)
        self.datalogger_id = rest[:10]
        return rest[10:]


@final
class C(B):
    record_type = 5
