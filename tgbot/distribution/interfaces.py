from abc import ABC, abstractmethod
from typing import Optional
from enum import Enum


class ProcessingStatus(str, Enum):
    CHOICED = "CHOICED"
    PREPARED = "PREPARED"
    CANCELED = "CANCELED"


class ICacheService(ABC):
    """Абстракция для работы с кэшем"""

    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        pass

    @abstractmethod
    async def set(self, key: str, value: str, ex: int = None) -> bool:
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        pass

    @abstractmethod
    async def set_nx(self, key: str, value: str, ex: int = None) -> bool:
        pass


class IDistributionRepository(ABC):
    """Абстракция для работы с распределениями"""

    @abstractmethod
    async def get_distribution(self, distribution_id: int):
        pass


class IChoiceRepository(ABC):
    """Абстракция для работы с выборами"""

    @abstractmethod
    async def get_user_choice(self, distribution_id: int, choice_index: int, user_id: int):
        pass

    @abstractmethod
    async def save_choice(self, distribution_id: int, button_index: int, user_id: int) -> None:
        pass

    @abstractmethod
    async def get_count_user_distribution_choices(self, distribution_id: int, user_id: int) -> int:
        pass


class IThrottlingService(ABC):
    """Абстракция для контроля частоты запросов"""

    @abstractmethod
    async def throttle_requests(self, user_lock_key: str) -> None:
        pass

    @abstractmethod
    async def unthrottle_requests(self, user_lock_key: str) -> None:
        pass

    @abstractmethod
    async def reserve_choice(self, choice_key: str, user_key: str) -> bool:
        pass

    @abstractmethod
    async def unreserve_choice(self, choice_key: str) -> None:
        pass


class ILimitService(ABC):
    """Абстракция для проверки лимитов"""

    @abstractmethod
    async def get_max_choices(self, distribution_id: int) -> int:
        pass

    @abstractmethod
    def check_choice_limit(self, user_current_choices: int, max_choices: int) -> None:
        pass


class IChoiceProcessor(ABC):
    """Абстракция для процессора выбора"""

    @abstractmethod
    async def start_processing(self) -> ProcessingStatus:
        pass

    @abstractmethod
    async def update_after_success(self) -> None:
        pass