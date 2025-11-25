#!/bin/bash
set -e

echo "Starting DevApply Celery Worker..."

# Wait for Redis to be ready
echo "Waiting for Redis..."
python3 << END
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

# Start Celery worker
echo "================================================================================"
echo "STARTING CELERY WORKER - Background Process Starting"
echo "================================================================================"
echo "Worker Configuration:"
echo "  - Concurrency: ${CELERY_CONCURRENCY:-2}"
echo "  - Max tasks per child: 1000"
echo "  - Time limit: 3600s"
echo "  - Soft time limit: 3000s"
echo "================================================================================"
exec celery -A celery_worker.celery worker \
    --loglevel=info \
    --concurrency=${CELERY_CONCURRENCY:-2} \
    --max-tasks-per-child=1000 \
    --time-limit=3600 \
    --soft-time-limit=3000
