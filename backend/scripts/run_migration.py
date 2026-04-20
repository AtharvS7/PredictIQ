"""Run the initial schema migration against Neon PostgreSQL."""
import asyncio
import asyncpg
import os
import sys

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_i5UIodKy6MYc@ep-soft-salad-ao7x2yo4-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
)

async def main():
    sql_path = os.path.join(os.path.dirname(__file__), "..", "migrations", "001_initial_schema.sql")
    sql_path = os.path.abspath(sql_path)

    if not os.path.exists(sql_path):
        print(f"ERROR: Migration file not found at {sql_path}")
        sys.exit(1)

    with open(sql_path, "r") as f:
        sql = f.read()

    print(f"Connecting to Neon PostgreSQL...")
    conn = await asyncpg.connect(DATABASE_URL, ssl="require")
    try:
        print("Running 001_initial_schema.sql ...")
        await conn.execute(sql)
        print("[OK] Schema migration completed successfully!")

        # Verify tables
        tables = await conn.fetch(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
        )
        print(f"\nTables in database ({len(tables)}):")
        for t in tables:
            print(f"  • {t['tablename']}")
    except Exception as e:
        print(f"[FAIL] Migration failed: {e}")
        sys.exit(1)
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
