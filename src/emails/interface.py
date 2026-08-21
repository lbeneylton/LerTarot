from abc import ABC, abstractmethod


class EmailSender(ABC):
    @abstractmethod
    async def send(self):...
        
        
        
class EmailSenderMock():
    pass
        
def get_sender():
    return EmailSenderMock()