
from dataclasses import dataclass
from typing import Final


class Message:
    addr64bit: str
    payload: str
    operation: str

    def __init__(self, addr64bit: str, operation: str, payload: str) -> None:
        self.addr64bit = addr64bit
        self.payload = payload
        self.operation = operation

    def __eq__(self, o: object) -> bool:
        if o == None: return False
        if ( isinstance(o, Message)):
            return self.operation == o.operation and self.addr64bit == o.addr64bit and self.payload == o.payload
        return False

    def __str__(self) -> str:
        return f'{self.operation}@{self.addr64bit}: {self.payload}'



class Ready(Message):

    operation: Final = 'READY'

    def __init__(self, addr64bit: str, payload: str) -> None:
        super().__init__(addr64bit, self.operation, payload)


class DataReq(Message):

    operation: Final = 'DATAREQ'

    def __init__(self, addr64bit: str, payload: str) -> None:
        super().__init__(addr64bit, self.operation, payload)


class Data(Message):

    operation: Final = 'DATA'

    def __init__(self, addr64bit: str, payload: str) -> None:
        super().__init__(addr64bit, self.operation, payload)


class DataAck(Message):

    operation: Final = 'DATAACK'

    def __init__(self, addr64bit: str, payload: str) -> None:
        super().__init__(addr64bit, self.operation, payload)
