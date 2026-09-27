import asyncio, os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
async def t():
    engine = create_async_engine('postgresql+asyncpg://jansetu_user:jansetu_password@127.0.0.1:5433/jansetu_db', echo=False)
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'schemes'"))
        print('Columns in schemes:', [r[0] for r in res.fetchall()])
asyncio.run(t())
