from abc import ABC, abstractmethod

class RateLimiter(ABC):
    @abstractmethod
    def is_allowed(self, key: str) -> bool:
        """Return True if request is allowed, False if rate limited."""
        pass