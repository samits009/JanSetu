import asyncio, os
from app.db.session import engine
from sqlalchemy import text
async def t():
    async with engine.connect() as conn:
        res = await conn.execute(text('SELECT COUNT(*) FROM welfare_applications'))
        print('COUNT:', res.scalar())
asyncio.run(t())
