from dataclasses import dataclass


@dataclass(init=False)
class Ack:
    """Acknowledge that a message was received."""
    result: int
