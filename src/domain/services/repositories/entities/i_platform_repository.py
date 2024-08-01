from typing import Union
from abc import ABC, abstractmethod
from src.core.models.config import Config
from src.domain.models.entities.platform.platform import Platform
from src.infrastructure.database.entities.platform_entity import PlatformEntity



class IPlatformRepository(ABC):
    @abstractmethod
    def save(
        self,
        config: Config,
        params: PlatformEntity,
    ) -> Union[Platform, None]:
        pass
