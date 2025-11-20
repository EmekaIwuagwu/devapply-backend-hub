#!/bin/bash
set -e

echo "=================================="
echo "DevApply Database Migration Script"
echo "=================================="
echo ""

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL environment variable is not set"
    echo "Please set it to your PostgreSQL connection string"
    exit 1
fi

echo "Database URL: ${DATABASE_URL:0:20}..." # Show first 20 chars only
echo ""

# Run migrations
echo "Running database migrations..."
flask db upgrade

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migrations completed successfully!"
    echo ""

    # Show current migration version
    echo "Current database version:"
    flask db current

    echo ""
    echo "All tables created:"
    python << 'END'
import os
import psycopg2
from urllib.parse import urlparse

url = urlparse(os.environ.get('DATABASE_URL'))
conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

cur = conn.cursor()
cur.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    ORDER BY table_name;
""")

tables = cur.fetchall()
for table in tables:
    print(f"  - {table[0]}")

cur.close()
conn.close()
END

    echo ""
    echo "=================================="
else
    echo ""
    echo "❌ Migration failed!"
    echo "Check the error messages above"
    exit 1
fi
