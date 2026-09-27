import asyncio
import asyncpg
import os

async def reset_db():
    password = os.environ.get("PGPASSWORD", "jansetu_password")
    conn = await asyncpg.connect(
        host='127.0.0.1', port=5433,
        user='jansetu_user', password=password,
        database='jansetu_db'
    )
    await conn.execute("DROP SCHEMA public CASCADE;")
    await conn.execute("CREATE SCHEMA public;")
    await conn.execute("GRANT ALL ON SCHEMA public TO jansetu_user;")
    await conn.execute("GRANT ALL ON SCHEMA public TO public;")
    await conn.close()
    print("Database reset.")

if __name__ == '__main__':
    asyncio.run(reset_db())
