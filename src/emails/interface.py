from abc import ABC, abstractmethod


class EmailSender(ABC):
    @abstractmethod
    async def send(self):...
        