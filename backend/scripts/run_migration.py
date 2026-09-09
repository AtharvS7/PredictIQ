"""Run the initial schema migration against Neon PostgreSQL."""
import asyncio
import os
import sys

import asyncpg


async def main():
    database_url = os.environ.get("DATABASE_URL", "").strip()
    if not database_url:
        print("ERROR: DATABASE_URL must be provided explicitly.", file=sys.stderr)
        return 1

    sql_path = os.path.join(os.path.dirname(__file__), "..", "migrations", "001_initial_schema.sql")
    sql_path = os.path.abspath(sql_path)

    if not os.path.exists(sql_path):
        print(f"ERROR: Migration file not found at {sql_path}")
        sys.exit(1)

    with open(sql_path, "r") as f:
        sql = f.read()

    print("Connecting to Neon PostgreSQL...")
    try:
        conn = await asyncpg.connect(database_url, ssl="require")
    except Exception:
        print("[FAIL] Database connection failed. Check credentials and connectivity.", file=sys.stderr)
        return 1
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
    except Exception:
        print("[FAIL] Migration failed. Inspect database server logs securely.", file=sys.stderr)
        sys.exit(1)
    finally:
        await conn.close()

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

