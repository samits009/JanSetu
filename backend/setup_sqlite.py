import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def reset_and_seed(db_url: str):
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from app.db.base import Base
    import app.models  # noqa: F401
    
    print(f"\nUsing: {db_url}")
    engine = create_async_engine(db_url, echo=False)
    
    print("\nDropping all tables...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    except Exception as e:
        print(f"  Warning during drop: {e}")
    
    print("Creating all tables...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"  Error creating tables: {e}")
        await engine.dispose()
        return False
    
    print("Running seed...")
    from app.db.seed import seed_database
    await seed_database()
    
    print("Seed complete!")
    await engine.dispose()
    return True

if __name__ == "__main__":
    db_url = "sqlite+aiosqlite:///./jansetu.db"
    asyncio.run(reset_and_seed(db_url))
