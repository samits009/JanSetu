"""
Database setup script for JanSetu development.
- Verifies the configured PostgreSQL connection
- Runs the canonical Alembic migrations
- Runs the seed/bootstrap logic
- Verifies integrity

Usage:
  python setup_db.py                        # tries jansetu creds directly
  python setup_db.py --pg-password=MyPass   # creates DB/user using postgres superuser
"""
import asyncio
import sys
import os
import argparse

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()


async def create_database_and_user(pg_password: str):
    """Create database and user using postgres superuser."""
    import asyncpg
    
    conn = await asyncpg.connect(
        host='127.0.0.1', port=5432,
        user='postgres', password=pg_password,
        database='postgres'
    )
    
    # Check/create user
    user_exists = await conn.fetchval(
        "SELECT 1 FROM pg_roles WHERE rolname = 'jansetu_user'"
    )
    if not user_exists:
        await conn.execute("CREATE USER jansetu_user WITH PASSWORD 'jansetu_password'")
        print("  Created user: jansetu_user")
    else:
        print("  User jansetu_user already exists")
    
    # Check/create database
    db_exists = await conn.fetchval(
        "SELECT 1 FROM pg_database WHERE datname = 'jansetu_db'"
    )
    if not db_exists:
        await conn.execute("CREATE DATABASE jansetu_db OWNER jansetu_user")
        print("  Created database: jansetu_db")
    else:
        print("  Database jansetu_db already exists")
    
    # Grant privileges
    await conn.execute("GRANT ALL PRIVILEGES ON DATABASE jansetu_db TO jansetu_user")
    await conn.close()
    
    # Also grant schema privileges
    conn2 = await asyncpg.connect(
        host='127.0.0.1', port=5432,
        user='postgres', password=pg_password,
        database='jansetu_db'
    )
    await conn2.execute("GRANT ALL ON SCHEMA public TO jansetu_user")
    await conn2.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO jansetu_user")
    await conn2.close()
    print("  Granted privileges")


async def test_connection(db_url: str) -> bool:
    """Test if we can connect to the database."""
    import asyncpg
    try:
        # Parse the asyncpg URL
        # postgresql+asyncpg://user:pass@host:port/db
        parts = db_url.replace("postgresql+asyncpg://", "")
        auth, rest = parts.split("@")
        user, password = auth.split(":")
        host_port, database = rest.split("/")
        host, port = host_port.split(":")
        
        conn = await asyncpg.connect(
            host=host, port=int(port),
            user=user, password=password,
            database=database
        )
        await conn.close()
        return True
    except Exception as e:
        print(f"  Connection failed: {e}")
        return False


async def reset_and_seed(db_url: str):
    """Upgrade the configured PostgreSQL database and seed it."""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from alembic.config import Config
    from alembic import command
    
    print(f"\nUsing: {db_url}")
    engine = create_async_engine(db_url, echo=False)
    
    print("\nApplying Alembic migrations...")
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", db_url.replace("postgresql+asyncpg", "postgresql"))
    command.upgrade(alembic_cfg, "head")
    print("  Migrations applied.\n")
    
    # Run seed
    print("Running seed...")
    from app.db.seed import seed_database
    await seed_database()
    
    # Verify integrity
    print("\n" + "=" * 60)
    print("VERIFYING SEED INTEGRITY")
    print("=" * 60)
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        from sqlalchemy import text
        
        # 1. Citizen
        result = await session.execute(text("SELECT id, name FROM citizens"))
        citizens = result.fetchall()
        print(f"\n✓ Citizens: {len(citizens)}")
        for c in citizens:
            print(f"    {c[0]} - {c[1]}")
        
        # 2. Schemes
        result = await session.execute(text("SELECT id, official_name, level, state FROM schemes"))
        schemes = result.fetchall()
        print(f"\n✓ Schemes: {len(schemes)}")
        for s in schemes:
            print(f"    {s[0]} - {s[1]} ({s[2]}, {s[3]})")
        
        # 3. Benefits
        result = await session.execute(text(
            "SELECT b.id, s.official_name, b.status FROM benefits b JOIN schemes s ON b.scheme_id = s.id"
        ))
        benefits = result.fetchall()
        print(f"\n✓ Benefits: {len(benefits)}")
        for b in benefits:
            print(f"    {b[1]} [{b[2]}]")
        
        # 4. Benefit Risks
        result = await session.execute(text("SELECT risk_type, description FROM benefit_risks"))
        risks = result.fetchall()
        print(f"\n✓ Benefit Risks: {len(risks)}")
        for r in risks:
            print(f"    {r[0]}: {r[1][:70]}")
        
        # 5. Applications
        result = await session.execute(text(
            "SELECT a.id, a.status, s.official_name FROM welfare_applications a JOIN schemes s ON a.scheme_id = s.id"
        ))
        apps = result.fetchall()
        print(f"\n✓ Applications: {len(apps)}")
        for a in apps:
            print(f"    {a[0]} - {a[2]} [{a[1]}]")
        
        # 6. ApplicationRequirements — THE KEY FIX VERIFICATION
        result = await session.execute(text(
            "SELECT ar.id, ar.application_id, ar.requirement_type, ar.description FROM application_requirements ar"
        ))
        reqs = result.fetchall()
        print(f"\n✓ ApplicationRequirements: {len(reqs)}")
        for r in reqs:
            print(f"    app:{r[1]} type:{r[2]} - {r[3]}")
        
        # Verify FK integrity: application_id points to welfare_applications
        result = await session.execute(text("""
            SELECT ar.id, wa.status 
            FROM application_requirements ar 
            JOIN welfare_applications wa ON ar.application_id = wa.id
        """))
        fk_check = result.fetchall()
        print(f"\n✓ ApplicationRequirement → WelfareApplication FK: {len(fk_check)} valid joins")
        
        if len(fk_check) != len(reqs):
            print("  ✗ INTEGRITY ERROR: Some requirements have invalid application_id!")
            await engine.dispose()
            return False
        else:
            print("    All FKs valid ✓")
        
        # 7. Documents & Evidence
        result = await session.execute(text("SELECT COUNT(*) FROM documents"))
        doc_count = result.scalar()
        result = await session.execute(text("SELECT COUNT(*) FROM evidence"))
        ev_count = result.scalar()
        print(f"\n✓ Documents: {doc_count}")
        print(f"✓ Evidence: {ev_count}")
        
        # 8. Eligibility Rules
        result = await session.execute(text(
            "SELECT er.rule_type, er.operator, er.value, s.official_name "
            "FROM scheme_eligibility_rules er JOIN schemes s ON er.scheme_id = s.id"
        ))
        rules = result.fetchall()
        print(f"\n✓ Eligibility Rules: {len(rules)}")
        for r in rules:
            print(f"    {r[3]}: {r[0]} {r[1]} {r[2]}")
        
        # 9. Locations
        result = await session.execute(text("SELECT location_type, district, state FROM locations"))
        locs = result.fetchall()
        print(f"\n✓ Locations: {len(locs)}")
        for l in locs:
            print(f"    {l[0]}: {l[1]}, {l[2]}")
    
    await engine.dispose()
    print("\n" + "=" * 60)
    print("SEED INTEGRITY CHECK PASSED ✓")
    print("=" * 60)
    return True


async def main():
    parser = argparse.ArgumentParser(description="JanSetu Database Setup")
    parser.add_argument("--pg-password", help="PostgreSQL superuser (postgres) password for creating DB/user")
    args = parser.parse_args()
    
    print("=" * 60)
    print("JanSetu Database Setup")
    print("=" * 60)
    
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not set in .env")
        sys.exit(1)
    
    # Try connecting directly first
    print("\nTesting database connection...")
    can_connect = await test_connection(db_url)
    
    if not can_connect:
        if args.pg_password:
            print("\nCreating database and user with postgres superuser...")
            try:
                await create_database_and_user(args.pg_password)
                can_connect = await test_connection(db_url)
            except Exception as e:
                print(f"Failed to create DB: {e}")
        
        if not can_connect:
            print("\n" + "=" * 60)
            print("Cannot connect to database.")
            print("Options:")
            print("  1. Run: python setup_db.py --pg-password=YOUR_POSTGRES_PASSWORD")
            print("  2. Manually create user/database:")
            print("     CREATE USER jansetu_user WITH PASSWORD 'jansetu_password';")
            print("     CREATE DATABASE jansetu_db OWNER jansetu_user;")
            print("     GRANT ALL PRIVILEGES ON DATABASE jansetu_db TO jansetu_user;")
            print("=" * 60)
            sys.exit(1)
    
    print("  Connection successful ✓")
    
    success = await reset_and_seed(db_url)
    if not success:
        print("Seed failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
