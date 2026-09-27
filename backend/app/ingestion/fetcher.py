import os
from abc import ABC, abstractmethod

class BaseFetcher(ABC):
    @abstractmethod
    async def fetch(self, source_url: str) -> str:
        pass

class LocalFixtureFetcher(BaseFetcher):
    """
    Fetches raw scheme content from local fixtures (txt/json/html).
    Used for the initial 10-20 seed schemes and testing.
    """
    def __init__(self, fixture_dir: str):
        self.fixture_dir = fixture_dir

    async def fetch(self, source_url: str) -> str:
        # We treat source_url as a filename if it's local
        filepath = os.path.join(self.fixture_dir, source_url)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Fixture not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

class WebFetcher(BaseFetcher):
    """
    Placeholder for future web scraping/fetching (e.g. using httpx).
    """
    async def fetch(self, source_url: str) -> str:
        raise NotImplementedError("Web fetching not enabled in Phase 5.")
