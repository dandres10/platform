# SPEC-006 T1
from abc import ABC, abstractmethod


class IEmailService(ABC):
    @abstractmethod
    async def send(self, to: str, subject: str, body: str) -> bool:
        pass
