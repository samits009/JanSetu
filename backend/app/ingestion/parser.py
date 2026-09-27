from abc import ABC, abstractmethod

class BaseParser(ABC):
    @abstractmethod
    def parse(self, raw_content: str) -> str:
        """Parses raw content into clean text for extraction."""
        pass

class TextParser(BaseParser):
    def parse(self, raw_content: str) -> str:
        # Just basic cleanup for text
        return raw_content.strip()

class HtmlParser(BaseParser):
    def parse(self, raw_content: str) -> str:
        # In the future, use BeautifulSoup to extract text from HTML
        raise NotImplementedError("HTML parsing not yet implemented.")
