import asyncio, asyncpg
async def t():
    conn = await asyncpg.connect('postgresql://jansetu_user:jansetu_password@127.0.0.1:5433/postgres')
    rows = await conn.fetch('SELECT datname FROM pg_database')
    print([r['datname'] for r in rows])
    await conn.close()
asyncio.run(t())
