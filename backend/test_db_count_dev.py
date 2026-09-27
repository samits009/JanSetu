import asyncio, os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
async def t():
    engine = create_async_engine('postgresql+asyncpg://jansetu_user:jansetu_password@127.0.0.1:5433/jansetu_db', echo=False)
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT COUNT(*) FROM welfare_applications"))
        print('welfare_applications count:', res.scalar())
        res = await conn.execute(text("SELECT COUNT(*) FROM citizens WHERE name = 'Ramesh Kumar'"))
        print('Ramesh count:', res.scalar())
asyncio.run(t())
