"""
Quick database fix script - adds missing columns to job_search_configs table
Run this on Render shell: python fix_database.py
"""
import os
from sqlalchemy import create_engine, text

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set")
    exit(1)

# Create engine
engine = create_engine(DATABASE_URL)

# SQL to add missing columns
sql = """
ALTER TABLE job_search_configs
  ADD COLUMN IF NOT EXISTS config_name VARCHAR(255),
  ADD COLUMN IF NOT EXISTS primary_job_type VARCHAR(50),
  ADD COLUMN IF NOT EXISTS primary_max_salary INTEGER,
  ADD COLUMN IF NOT EXISTS primary_remote_preference VARCHAR(50),
  ADD COLUMN IF NOT EXISTS secondary_job_type VARCHAR(50),
  ADD COLUMN IF NOT EXISTS secondary_max_salary INTEGER,
  ADD COLUMN IF NOT EXISTS secondary_remote_preference VARCHAR(50);
"""

try:
    with engine.connect() as conn:
        print("Connecting to database...")
        conn.execute(text(sql))
        conn.commit()
        print("✅ Successfully added missing columns!")
        print("\nAdded columns:")
        print("  - config_name")
        print("  - primary_job_type")
        print("  - primary_max_salary")
        print("  - primary_remote_preference")
        print("  - secondary_job_type")
        print("  - secondary_max_salary")
        print("  - secondary_remote_preference")
        print("\n🎉 Database updated! Restart your backend server.")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
