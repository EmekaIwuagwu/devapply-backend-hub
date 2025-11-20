"""
Database Migration Runner

This script runs Flask-Migrate database migrations automatically.
It can be run standalone or imported into your startup process.
"""
import os
import sys
import time
import logging
from subprocess import run, CalledProcessError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_database_connection(max_retries=30, retry_delay=2):
    """Check if database is accessible"""
    import psycopg2
    from urllib.parse import urlparse

    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        logger.error("DATABASE_URL environment variable not set!")
        return False

    url = urlparse(database_url)
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
            logger.info("✅ Database connection successful!")
            return True
        except psycopg2.OperationalError as e:
            retry_count += 1
            logger.warning(f"Database not ready yet. Retrying... ({retry_count}/{max_retries})")
            time.sleep(retry_delay)

    logger.error("❌ Could not connect to database after maximum retries!")
    return False


def run_migrations():
    """Run Flask-Migrate database migrations"""
    logger.info("=" * 60)
    logger.info("Running Database Migrations")
    logger.info("=" * 60)

    try:
        # Run flask db upgrade
        result = run(
            ['flask', 'db', 'upgrade'],
            capture_output=True,
            text=True,
            check=True
        )

        logger.info(result.stdout)
        if result.stderr:
            logger.warning(result.stderr)

        logger.info("✅ Migrations completed successfully!")
        return True

    except CalledProcessError as e:
        logger.error("❌ Migration failed!")
        logger.error(f"stdout: {e.stdout}")
        logger.error(f"stderr: {e.stderr}")
        return False
    except FileNotFoundError:
        logger.error("❌ Flask command not found! Make sure Flask is installed.")
        return False


def check_tables_exist():
    """Verify that tables were created"""
    import psycopg2
    from urllib.parse import urlparse

    try:
        database_url = os.environ.get('DATABASE_URL')
        url = urlparse(database_url)

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
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)

        tables = cur.fetchall()

        if tables:
            logger.info(f"✅ Found {len(tables)} tables in database:")
            for table in tables:
                logger.info(f"   - {table[0]}")
        else:
            logger.warning("⚠️  No tables found in database!")

        cur.close()
        conn.close()

        return len(tables) > 0

    except Exception as e:
        logger.error(f"❌ Error checking tables: {e}")
        return False


def get_current_migration():
    """Get current migration version"""
    try:
        result = run(
            ['flask', 'db', 'current'],
            capture_output=True,
            text=True,
            check=True
        )

        logger.info("Current migration version:")
        logger.info(result.stdout)

        return True

    except CalledProcessError as e:
        logger.error("❌ Could not get current migration version")
        logger.error(e.stderr)
        return False


def main():
    """Main migration runner"""
    logger.info("🚀 DevApply Database Migration Script")
    logger.info("")

    # Step 1: Check database connection
    logger.info("Step 1: Checking database connection...")
    if not check_database_connection():
        logger.error("Cannot proceed without database connection!")
        sys.exit(1)

    logger.info("")

    # Step 2: Run migrations
    logger.info("Step 2: Running migrations...")
    if not run_migrations():
        logger.error("Migration failed!")
        sys.exit(1)

    logger.info("")

    # Step 3: Verify tables
    logger.info("Step 3: Verifying tables...")
    if not check_tables_exist():
        logger.warning("Tables verification failed, but migration reported success")

    logger.info("")

    # Step 4: Show current version
    logger.info("Step 4: Checking current migration version...")
    get_current_migration()

    logger.info("")
    logger.info("=" * 60)
    logger.info("✅ Migration process completed successfully!")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
