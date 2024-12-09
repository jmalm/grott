from dataclasses import dataclass

from .message import MessageWithRecordType
from .response import Response
from .single_register_messages import SingleRegisterValueMessage


@dataclass(init=False)
class InverterGetResponse(SingleRegisterValueMessage, Response, MessageWithRecordType):
    RECORD_TYPE = 5
    is_encrypted_ack = True

    @property
    def response(self):
        return {"value": self.value}
