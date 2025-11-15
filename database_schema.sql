-- DevApply Database Schema
-- Run this script in your Render PostgreSQL database to create all tables

-- =============================================================================
-- DROP TABLES (if you want to start fresh - UNCOMMENT CAREFULLY!)
-- =============================================================================
-- DROP TABLE IF EXISTS automation_logs CASCADE;
-- DROP TABLE IF EXISTS job_queue CASCADE;
-- DROP TABLE IF EXISTS job_listings CASCADE;
-- DROP TABLE IF EXISTS job_search_configs CASCADE;
-- DROP TABLE IF EXISTS platform_credentials CASCADE;
-- DROP TABLE IF EXISTS applications CASCADE;
-- DROP TABLE IF EXISTS resumes CASCADE;
-- DROP TABLE IF EXISTS user_preferences CASCADE;
-- DROP TABLE IF EXISTS payments CASCADE;
-- DROP TABLE IF EXISTS subscriptions CASCADE;
-- DROP TABLE IF EXISTS platforms CASCADE;
-- DROP TABLE IF EXISTS users CASCADE;

-- =============================================================================
-- CREATE TABLES
-- =============================================================================

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    full_name VARCHAR(255),
    phone VARCHAR(50),
    location VARCHAR(255),
    linkedin_url VARCHAR(500),
    github_url VARCHAR(500),
    portfolio_url VARCHAR(500),
    current_role VARCHAR(255),
    years_experience INTEGER,
    preferred_job_type VARCHAR(50),
    salary_expectations VARCHAR(100),
    professional_bio TEXT,
    skills TEXT[],
    avatar_base64 TEXT,
    oauth_provider VARCHAR(50),
    oauth_id VARCHAR(255),
    email_verified BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR(255),
    email_verification_sent_at TIMESTAMP,
    password_reset_token VARCHAR(255),
    password_reset_sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);
CREATE INDEX IF NOT EXISTS ix_users_oauth_provider_oauth_id ON users(oauth_provider, oauth_id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email_verification_token ON users(email_verification_token) WHERE email_verification_token IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS ix_users_password_reset_token ON users(password_reset_token) WHERE password_reset_token IS NOT NULL;

-- Subscriptions Table
CREATE TABLE IF NOT EXISTS subscriptions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    applications_limit INTEGER,
    applications_used INTEGER DEFAULT 0,
    billing_cycle VARCHAR(20),
    amount FLOAT,
    currency VARCHAR(3) DEFAULT 'USD',
    next_billing_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_subscriptions_user_id ON subscriptions(user_id);

-- Payments Table
CREATE TABLE IF NOT EXISTS payments (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subscription_id VARCHAR(36) REFERENCES subscriptions(id) ON DELETE SET NULL,
    amount FLOAT NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(50) NOT NULL,
    payment_method VARCHAR(50),
    transaction_id VARCHAR(255),
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_payments_user_id ON payments(user_id);

-- Resumes Table
CREATE TABLE IF NOT EXISTS resumes (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_base64 TEXT NOT NULL,
    file_type VARCHAR(10),
    file_size INTEGER,
    is_default BOOLEAN DEFAULT FALSE,
    job_type_tag VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_resumes_user_id ON resumes(user_id);

-- Applications Table
CREATE TABLE IF NOT EXISTS applications (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company_name VARCHAR(255) NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    job_type VARCHAR(100),
    location VARCHAR(255),
    salary_range VARCHAR(100),
    status VARCHAR(50) NOT NULL DEFAULT 'sent',
    platform VARCHAR(50) NOT NULL,
    job_url VARCHAR(1000),
    resume_used_id VARCHAR(36) REFERENCES resumes(id) ON DELETE SET NULL,
    cover_letter TEXT,
    notes TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_status_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_applications_user_id ON applications(user_id);
CREATE INDEX IF NOT EXISTS ix_applications_platform ON applications(platform);
CREATE INDEX IF NOT EXISTS ix_applications_status ON applications(status);

-- Platform Credentials Table
CREATE TABLE IF NOT EXISTS platform_credentials (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    username VARCHAR(255) NOT NULL,
    encrypted_password TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_verified TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_platform UNIQUE (user_id, platform)
);

CREATE INDEX IF NOT EXISTS ix_platform_credentials_user_id ON platform_credentials(user_id);

-- Job Search Configs Table
CREATE TABLE IF NOT EXISTS job_search_configs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platforms TEXT[],
    primary_job_title VARCHAR(255),
    primary_location VARCHAR(255),
    primary_min_salary INTEGER,
    primary_experience_level VARCHAR(50),
    primary_keywords TEXT[],
    primary_resume_id VARCHAR(36) REFERENCES resumes(id) ON DELETE SET NULL,
    secondary_job_title VARCHAR(255),
    secondary_location VARCHAR(255),
    secondary_min_salary INTEGER,
    secondary_experience_level VARCHAR(50),
    secondary_keywords TEXT[],
    secondary_resume_id VARCHAR(36) REFERENCES resumes(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_job_search_configs_user_id ON job_search_configs(user_id);

-- Platforms Table
CREATE TABLE IF NOT EXISTS platforms (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    logo_url VARCHAR(500),
    is_enabled BOOLEAN DEFAULT TRUE,
    is_popular BOOLEAN DEFAULT FALSE,
    requires_credentials BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_platforms_code ON platforms(code);

-- Job Listings Table
CREATE TABLE IF NOT EXISTS job_listings (
    id VARCHAR(36) PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    external_id VARCHAR(255),
    company_name VARCHAR(255) NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    salary_min INTEGER,
    salary_max INTEGER,
    job_type VARCHAR(100),
    description TEXT,
    requirements TEXT,
    job_url VARCHAR(1000) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    posted_at TIMESTAMP,
    CONSTRAINT uq_platform_external_id UNIQUE (platform, external_id)
);

CREATE INDEX IF NOT EXISTS ix_job_listings_platform ON job_listings(platform);

-- Job Queue Table
CREATE TABLE IF NOT EXISTS job_queue (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_search_config_id VARCHAR(36) REFERENCES job_search_configs(id) ON DELETE SET NULL,
    platform VARCHAR(50) NOT NULL,
    job_listing_id VARCHAR(36) REFERENCES job_listings(id) ON DELETE SET NULL,
    company_name VARCHAR(255) NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    job_url VARCHAR(1000) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    priority INTEGER DEFAULT 5,
    match_score INTEGER,
    scheduled_for TIMESTAMP,
    processed_at TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_job_queue_user_id ON job_queue(user_id);
CREATE INDEX IF NOT EXISTS ix_job_queue_status ON job_queue(status);

-- Automation Logs Table
CREATE TABLE IF NOT EXISTS automation_logs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_queue_id VARCHAR(36) REFERENCES job_queue(id) ON DELETE SET NULL,
    action_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL,
    details TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_automation_logs_user_id ON automation_logs(user_id);
CREATE INDEX IF NOT EXISTS ix_automation_logs_action_type ON automation_logs(action_type);

-- User Preferences Table
CREATE TABLE IF NOT EXISTS user_preferences (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    email_notifications_enabled BOOLEAN DEFAULT TRUE,
    daily_summary_enabled BOOLEAN DEFAULT TRUE,
    application_updates_enabled BOOLEAN DEFAULT TRUE,
    job_matches_enabled BOOLEAN DEFAULT TRUE,
    marketing_emails_enabled BOOLEAN DEFAULT FALSE,
    auto_apply_enabled BOOLEAN DEFAULT TRUE,
    max_applications_per_day INTEGER DEFAULT 20,
    min_match_score INTEGER DEFAULT 70,
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'en',
    currency VARCHAR(3) DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_user_preferences_user_id ON user_preferences(user_id);

-- Alembic Version Table (for migration tracking)
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL PRIMARY KEY
);

-- Insert current migration version
INSERT INTO alembic_version (version_num) VALUES ('20251115_072114')
ON CONFLICT (version_num) DO NOTHING;

-- =============================================================================
-- SEED DATA - Platforms
-- =============================================================================

INSERT INTO platforms (id, name, code, is_enabled, is_popular, requires_credentials) VALUES
    (gen_random_uuid()::text, 'LinkedIn', 'linkedin', TRUE, TRUE, TRUE),
    (gen_random_uuid()::text, 'Indeed', 'indeed', TRUE, TRUE, TRUE),
    (gen_random_uuid()::text, 'Glassdoor', 'glassdoor', TRUE, TRUE, TRUE),
    (gen_random_uuid()::text, 'ZipRecruiter', 'ziprecruiter', TRUE, FALSE, TRUE),
    (gen_random_uuid()::text, 'Monster', 'monster', TRUE, FALSE, TRUE),
    (gen_random_uuid()::text, 'CareerBuilder', 'careerbuilder', TRUE, FALSE, TRUE),
    (gen_random_uuid()::text, 'Dice', 'dice', TRUE, FALSE, TRUE),
    (gen_random_uuid()::text, 'AngelList', 'angellist', TRUE, FALSE, TRUE)
ON CONFLICT (code) DO NOTHING;

-- =============================================================================
-- VERIFY TABLES CREATED
-- =============================================================================

SELECT
    'Table created: ' || tablename as status
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

-- Count check
SELECT
    COUNT(*) as total_tables,
    'Expected: 13 tables (users, subscriptions, payments, resumes, applications, platform_credentials, job_search_configs, platforms, job_listings, job_queue, automation_logs, user_preferences, alembic_version)' as note
FROM pg_tables
WHERE schemaname = 'public';
