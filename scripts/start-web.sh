#!/bin/bash
set -e

echo "Starting DevApply Web Server..."

# Wait for database to be ready
echo "Waiting for database..."
python3 << END
import time
import psycopg2
import os
from urllib.parse import urlparse

url = urlparse(os.environ.get('DATABASE_URL'))
max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        conn.close()
        print("Database is ready!")
        break
    except psycopg2.OperationalError:
        retry_count += 1
        print(f"Database not ready yet. Retrying... ({retry_count}/{max_retries})")
        time.sleep(2)
else:
    print("Could not connect to database!")
    exit(1)
END

# Run database migrations using Python script
echo "Running database migrations..."
python3 scripts/run_migrations.py || {
    echo "Python migration script failed, trying direct flask command..."
    python3 -m flask db upgrade || echo "Migrations failed or already up to date"
}

# Seed platforms if needed
echo "Seeding platforms..."
python3 -m flask seed_platforms || echo "Platforms already seeded"

# Start Gunicorn
echo "Starting Gunicorn server..."
exec gunicorn \
    --bind 0.0.0.0:${PORT:-5000} \
    --workers ${WEB_WORKERS:-4} \
    --threads ${WEB_THREADS:-2} \
    --timeout ${WEB_TIMEOUT:-120} \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    run:app
