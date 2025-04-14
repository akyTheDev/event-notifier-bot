"""Service factory module."""

from functools import lru_cache

from service.event_service import EventService


class ServiceFactory:
    """Service factory class."""

    @staticmethod
    @lru_cache
    def create_event_service() -> EventService:
        """Create event service(Singleton.)."""
        return EventService()
