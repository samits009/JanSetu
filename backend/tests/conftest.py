import pytest
import pytest_asyncio
import os
import asyncio
import asyncpg
from urllib.parse import urlparse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from alembic.config import Config
from alembic import command
from dotenv import load_dotenv

# Load .env before importing app modules (TEST_DATABASE_URL, DEV_DEMO_AUTH, etc.)
load_dotenv()
# Test fixtures are permitted to use demo-login compatibility tooling per Req #1 & #15
os.environ["DEV_DEMO_AUTH"] = "true"

# We need the app and get_async_db to override it
from app.main import app
from app.db.session import get_async_db

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

def run_migrations(connection_url: str):
    """Run Alembic migrations to current head on the given database."""
    alembic_cfg = Config("alembic.ini")
    sync_url = connection_url.replace("postgresql+asyncpg://", "postgresql://")
    alembic_cfg.set_main_option("sqlalchemy.url", sync_url)
    command.upgrade(alembic_cfg, "head")

async def ensure_test_database(url: str):
    parsed = urlparse(url)
    db_name = parsed.path.lstrip('/')
    
    sys_url = url.replace(f"/{db_name}", "/postgres")
    sys_url = sys_url.replace("postgresql+asyncpg://", "postgresql://")
    
    conn = await asyncpg.connect(sys_url)
    exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", db_name)
    if not exists:
        await conn.execute(f'CREATE DATABASE "{db_name}"')
    
    await conn.execute(f'GRANT ALL PRIVILEGES ON DATABASE "{db_name}" TO jansetu_user')
    await conn.close()

@pytest_asyncio.fixture(loop_scope="session")
async def engine():
    # 1. FAIL FAST ON MISSING TEST DATABASE CONFIG
    db_url = os.environ.get("TEST_DATABASE_URL")
    if not db_url:
        # Fallback ONLY if explicitly documented, but we must enforce the name is jansetu_test
        db_url = "postgresql+asyncpg://jansetu_user:jansetu_password@127.0.0.1:5433/jansetu_test"
    
    # 2. DEVELOPMENT DATABASE SAFETY & DATABASE VALIDATION
    parsed = urlparse(db_url)
    db_name = parsed.path.lstrip('/')
    
    if db_name == "jansetu_db":
        raise ValueError("CRITICAL ERROR: TEST_DATABASE_URL is pointing to jansetu_db. Aborting to protect development data.")
    
    if not db_name.endswith("test"):
        raise ValueError(f"TEST_DATABASE_URL database name '{db_name}' does not look like a test database.")

    # 7. DATABASE VALIDATION - ONLY THEN permit test schema setup
    await ensure_test_database(db_url)
    
    # Clean the entire public schema and recreate with a standalone connection
    clean_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(clean_url)
    await conn.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO public;")
    await conn.close()
        
    # 3. MIGRATIONS - use Alembic instead of create_all
    run_migrations(db_url)
    
    # 4. SEEDING - seed using the canonical logic
    from app.db.seed import seed_database
    await seed_database(db_url)
    
    test_engine = create_async_engine(db_url, echo=False)
    
    yield test_engine
    
    # 8. TEST LIFECYCLE - Clean only the test database/schema
    await test_engine.dispose()
    conn = await asyncpg.connect(clean_url)
    await conn.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO public;")
    await conn.close()

@pytest_asyncio.fixture
async def db_session(engine):
    """Yield a database session. It wraps the test in a transaction and rolls it back."""
    connection = await engine.connect()
    transaction = await connection.begin()
    
    async_session = AsyncSession(bind=connection, expire_on_commit=False)
    
    # 5. FASTAPI DEPENDENCY OVERRIDE
    async def override_get_async_db():
        yield async_session
        
    app.dependency_overrides[get_async_db] = override_get_async_db
    
    yield async_session
    
    # Verify that dependency override is removed/cleared after the test session
    app.dependency_overrides.clear()
    
    await async_session.close()
    await transaction.rollback()
    await connection.close()
