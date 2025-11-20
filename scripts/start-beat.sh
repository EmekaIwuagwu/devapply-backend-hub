#!/bin/bash
set -e

echo "Starting DevApply Celery Beat Scheduler..."

# Wait for Redis to be ready
echo "Waiting for Redis..."
python << END
import time
import redis
import os
from urllib.parse import urlparse

url = urlparse(os.environ.get('CELERY_BROKER_URL', os.environ.get('REDIS_URL')))
max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        r = redis.Redis(host=url.hostname, port=url.port or 6379, db=0)
        r.ping()
        print("Redis is ready!")
        break
    except redis.ConnectionError:
        retry_count += 1
        print(f"Redis not ready yet. Retrying... ({retry_count}/{max_retries})")
        time.sleep(2)
else:
    print("Could not connect to Redis!")
    exit(1)
END

# Remove any existing beat schedule database
rm -f celerybeat-schedule

# Start Celery beat
echo "================================================================================"
echo "STARTING CELERY BEAT SCHEDULER - Periodic Task Scheduler Starting"
echo "================================================================================"
exec celery -A celery_worker.celery beat \
    --loglevel=info \
    --pidfile=/tmp/celerybeat.pid
