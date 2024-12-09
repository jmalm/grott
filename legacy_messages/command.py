from __future__ import annotations

from messages.response import Response
from messages.message import Message


class Command(Message):
    response: Response
