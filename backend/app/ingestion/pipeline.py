from sqlalchemy.ext.asyncio import AsyncSession
from app.ingestion.fetcher import LocalFixtureFetcher
from app.ingestion.parser import TextParser
from app.ingestion.extractor import DeterministicExtractor
from app.ingestion.normalizer import Normalizer
from app.ingestion.validator import Validator
from app.ingestion.policy_compiler import PolicyCompiler
from app.models.scheme import SchemeSource

class IngestionPipeline:
    def __init__(self, session: AsyncSession, fixture_dir: str):
        self.session = session
        self.fetcher = LocalFixtureFetcher(fixture_dir)
        self.parser = TextParser()
        self.extractor = DeterministicExtractor()
        self.normalizer = Normalizer()
        self.validator = Validator()
        self.compiler = PolicyCompiler(session)

    async def ingest_source(self, source: SchemeSource) -> None:
        """
        End-to-end ingestion of a single source.
        """
        # 1. Fetch
        raw_content = await self.fetcher.fetch(source.source_url)
        
        # 2. Parse
        clean_content = self.parser.parse(raw_content)
        
        # 3. Extract
        extracted = await self.extractor.extract(clean_content)
        
        # 4. Normalize
        normalized = self.normalizer.normalize(extracted)
        
        # 5. Validate
        status = self.validator.validate(normalized)
        
        # 6. Compile & Version
        scheme = await self.compiler.compile(normalized, source, status)
        
        return scheme
