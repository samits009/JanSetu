import asyncio
import asyncpg
import sys
import os

async def try_current_user():
    user = os.environ.get("USERNAME", "samit")
    try:
        conn = await asyncpg.connect(host='127.0.0.1', port=5432, user=user, database='postgres')
        print(f"SUCCESS with user: {user}")
        await conn.execute("CREATE USER jansetu_user WITH PASSWORD 'jansetu_password'")
        await conn.execute("CREATE DATABASE jansetu_db OWNER jansetu_user")
        await conn.execute("GRANT ALL PRIVILEGES ON DATABASE jansetu_db TO jansetu_user")
        print("DB setup complete")
        await conn.close()
        sys.exit(0)
    except Exception as e:
        print(f"FAILED with user {user}: {e}")
    
    # Try empty password for postgres just in case asyncpg needs explicitly empty
    try:
        conn = await asyncpg.connect(host='127.0.0.1', port=5432, user='postgres', database='postgres')
        print("SUCCESS with postgres (no password)")
        await conn.close()
    except Exception as e:
        print(f"FAILED postgres no password: {e}")
    
if __name__ == '__main__':
    asyncio.run(try_current_user())
