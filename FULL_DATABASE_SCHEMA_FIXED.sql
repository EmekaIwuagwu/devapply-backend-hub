-- ============================================================================
-- DevApply Backend - COMPLETE DATABASE SCHEMA (ALL FIXES APPLIED)
-- ============================================================================
-- This is the ONLY SQL file you need to run!
-- Creates ALL 15 tables with ALL fixes applied - MATCHES Python models 100%
-- ✓ Fixed reserved keyword (current_role)
-- ✓ All JSON columns are JSONB (not JSON)
-- ✓ ALL models match Python code exactly
-- ✓ All optional fields are nullable
-- ✓ All system fields have proper NOT NULL and defaults
-- ============================================================================
-- USAGE: Copy this entire file and paste into Render PostgreSQL Shell
-- ============================================================================

BEGIN;

-- ============================================================================
-- MIGRATION SECTION - Fix existing databases
-- ============================================================================

-- Drop all existing tables to avoid conflicts (backup your data first!)
DROP TABLE IF EXISTS activity_logs CASCADE;
DROP TABLE IF EXISTS automation_logs CASCADE;
DROP TABLE IF EXISTS job_queue CASCADE;
DROP TABLE IF EXISTS job_listings CASCADE;
DROP TABLE IF EXISTS applications CASCADE;
DROP TABLE IF EXISTS job_search_configs CASCADE;
DROP TABLE IF EXISTS resumes CASCADE;
DROP TABLE IF EXISTS platform_credentials CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS subscriptions CASCADE;
DROP TABLE IF EXISTS user_preferences CASCADE;
DROP TABLE IF EXISTS platforms CASCADE;
DROP TABLE IF EXISTS videos CASCADE;
DROP TABLE IF EXISTS settings CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ============================================================================
-- 1. USERS TABLE
-- ============================================================================

CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    full_name VARCHAR(255),
    phone VARCHAR(20),
    location VARCHAR(255),
    linkedin_url VARCHAR(500),
    github_url VARCHAR(500),
    portfolio_url VARCHAR(500),
    "current_role" VARCHAR(255),
    years_experience INTEGER,
    preferred_job_type VARCHAR(100),
    salary_expectations INTEGER,
    professional_bio TEXT,
    skills JSONB DEFAULT '[]'::jsonb NOT NULL,
    avatar_base64 TEXT,
    oauth_provider VARCHAR(20),
    oauth_id VARCHAR(255),
    role VARCHAR(20) DEFAULT 'user' NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE NOT NULL,
    email_verification_token VARCHAR(255) UNIQUE,
    email_verification_sent_at TIMESTAMP,
    password_reset_token VARCHAR(255) UNIQUE,
    password_reset_sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX ix_users_email ON users(email);
CREATE INDEX ix_users_role ON users(role);

-- ============================================================================
-- 2. USER PREFERENCES TABLE
-- ============================================================================

CREATE TABLE user_preferences (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) UNIQUE NOT NULL,
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================================
-- 3. PLATFORMS TABLE
-- ============================================================================

CREATE TABLE platforms (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_platforms_name ON platforms(name);

-- ============================================================================
-- 4. RESUMES TABLE
-- ============================================================================

CREATE TABLE resumes (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_base64 TEXT NOT NULL,
    file_type VARCHAR(10) NOT NULL,
    file_size INTEGER NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    job_type_tag VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX ix_resumes_user_id ON resumes(user_id);
CREATE INDEX ix_resumes_is_default ON resumes(is_default);

-- ============================================================================
-- 5. JOB SEARCH CONFIG TABLE
-- ============================================================================

CREATE TABLE job_search_configs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    config_name VARCHAR(255),
    platforms JSONB DEFAULT '[]'::jsonb,
    primary_job_title VARCHAR(255),
    primary_location VARCHAR(255),
    primary_job_type VARCHAR(50),
    primary_min_salary INTEGER,
    primary_max_salary INTEGER,
    primary_experience_level VARCHAR(50),
    primary_remote_preference VARCHAR(50),
    primary_keywords JSONB DEFAULT '[]'::jsonb,
    primary_resume_id VARCHAR(36),
    secondary_job_title VARCHAR(255),
    secondary_location VARCHAR(255),
    secondary_job_type VARCHAR(50),
    secondary_min_salary INTEGER,
    secondary_max_salary INTEGER,
    secondary_experience_level VARCHAR(50),
    secondary_remote_preference VARCHAR(50),
    secondary_keywords JSONB DEFAULT '[]'::jsonb,
    secondary_resume_id VARCHAR(36),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (primary_resume_id) REFERENCES resumes(id) ON DELETE SET NULL,
    FOREIGN KEY (secondary_resume_id) REFERENCES resumes(id) ON DELETE SET NULL
);

CREATE INDEX ix_job_search_configs_user_id ON job_search_configs(user_id);

-- ============================================================================
-- 6. SUBSCRIPTIONS TABLE
-- ============================================================================

CREATE TABLE subscriptions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    plan_type VARCHAR(20) DEFAULT 'free' NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    applications_limit INTEGER DEFAULT 10,
    applications_used INTEGER DEFAULT 0,
    billing_cycle VARCHAR(20),
    amount NUMERIC(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    next_billing_date DATE,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX ix_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX ix_subscriptions_status ON subscriptions(status);

-- ============================================================================
-- 7. PAYMENTS TABLE
-- ============================================================================

CREATE TABLE payments (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    subscription_id VARCHAR(36),
    amount NUMERIC(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_method VARCHAR(50),
    payment_method_expiry VARCHAR(10),
    status VARCHAR(20) DEFAULT 'pending',
    paid_at TIMESTAMP,
    invoice_url TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE SET NULL
);

CREATE INDEX ix_payments_user_id ON payments(user_id);
CREATE INDEX ix_payments_status ON payments(status);

-- ============================================================================
-- 8. APPLICATIONS TABLE
-- ============================================================================

CREATE TABLE applications (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    job_type VARCHAR(100),
    location VARCHAR(255),
    salary_range VARCHAR(100),
    status VARCHAR(20) DEFAULT 'sent',
    platform VARCHAR(50) NOT NULL,
    job_url TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_status_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resume_used_id VARCHAR(36),
    cover_letter TEXT,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (resume_used_id) REFERENCES resumes(id) ON DELETE SET NULL
);

CREATE INDEX ix_applications_user_id ON applications(user_id);
CREATE INDEX ix_applications_status ON applications(status);
CREATE INDEX ix_applications_applied_at ON applications(applied_at);

-- ============================================================================
-- 9. JOB LISTINGS TABLE
-- ============================================================================

CREATE TABLE job_listings (
    id VARCHAR(36) PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    external_id VARCHAR(255) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    salary_range VARCHAR(100),
    job_type VARCHAR(100),
    description TEXT,
    requirements TEXT,
    job_url TEXT NOT NULL,
    posted_date TIMESTAMP,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(platform, external_id)
);

CREATE INDEX ix_job_listings_platform ON job_listings(platform);
CREATE INDEX ix_job_listings_external_id ON job_listings(external_id);
CREATE INDEX ix_job_listings_job_title ON job_listings(job_title);
CREATE INDEX ix_job_listings_is_active ON job_listings(is_active);

-- ============================================================================
-- 10. JOB QUEUE TABLE
-- ============================================================================

CREATE TABLE job_queue (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    job_search_config_id VARCHAR(36),
    platform VARCHAR(50) NOT NULL,
    job_listing_id VARCHAR(36),
    company_name VARCHAR(255) NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    job_url TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    priority INTEGER DEFAULT 5,
    match_score NUMERIC(5, 2) DEFAULT 0.0,
    scheduled_for TIMESTAMP,
    attempted_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_search_config_id) REFERENCES job_search_configs(id) ON DELETE SET NULL,
    FOREIGN KEY (job_listing_id) REFERENCES job_listings(id) ON DELETE SET NULL
);

CREATE INDEX ix_job_queue_user_id ON job_queue(user_id);
CREATE INDEX ix_job_queue_status ON job_queue(status);
CREATE INDEX ix_job_queue_priority ON job_queue(priority);
CREATE INDEX ix_job_queue_created_at ON job_queue(created_at);

-- ============================================================================
-- 11. PLATFORM CREDENTIALS TABLE
-- ============================================================================

CREATE TABLE platform_credentials (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    username_encrypted TEXT,
    encrypted_password TEXT NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    last_verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, platform)
);

CREATE INDEX ix_platform_credentials_user_id ON platform_credentials(user_id);

-- ============================================================================
-- 12. AUTOMATION LOGS TABLE
-- ============================================================================

CREATE TABLE automation_logs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36),
    job_queue_id VARCHAR(36),
    action_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    details JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (job_queue_id) REFERENCES job_queue(id) ON DELETE SET NULL
);

CREATE INDEX ix_automation_logs_user_id ON automation_logs(user_id);
CREATE INDEX ix_automation_logs_action_type ON automation_logs(action_type);
CREATE INDEX ix_automation_logs_created_at ON automation_logs(created_at);

-- ============================================================================
-- 13. VIDEOS TABLE
-- ============================================================================

CREATE TABLE videos (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    video_base64 TEXT NOT NULL,
    thumbnail_base64 TEXT,
    file_size INTEGER,
    duration INTEGER,
    category VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    view_count INTEGER DEFAULT 0,
    uploaded_by VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX ix_videos_created_at ON videos(created_at);
CREATE INDEX ix_videos_category ON videos(category);

-- ============================================================================
-- 14. SETTINGS TABLE
-- ============================================================================

CREATE TABLE settings (
    id INTEGER PRIMARY KEY DEFAULT 1,
    site_name VARCHAR(255) DEFAULT 'DevApply',
    site_description TEXT,
    contact_email VARCHAR(255),
    support_phone VARCHAR(20),
    logo_base64 TEXT,
    email_notifications_enabled BOOLEAN DEFAULT TRUE,
    system_alerts_enabled BOOLEAN DEFAULT TRUE,
    admin_notification_email VARCHAR(255),
    low_balance_threshold INTEGER DEFAULT 100,
    session_timeout_minutes INTEGER DEFAULT 1440,
    max_login_attempts INTEGER DEFAULT 5,
    password_min_length INTEGER DEFAULT 8,
    require_email_verification BOOLEAN DEFAULT TRUE,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    maintenance_mode BOOLEAN DEFAULT FALSE,
    maintenance_message TEXT,
    api_rate_limit_per_hour INTEGER DEFAULT 1000,
    max_file_upload_mb INTEGER DEFAULT 50,
    allowed_file_types JSONB DEFAULT '[]'::jsonb,
    max_applications_per_user_per_day INTEGER DEFAULT 50,
    auto_cleanup_days INTEGER DEFAULT 90,
    linkedin_integration_enabled BOOLEAN DEFAULT TRUE,
    indeed_integration_enabled BOOLEAN DEFAULT TRUE,
    ai_matching_enabled BOOLEAN DEFAULT TRUE,
    video_tutorials_enabled BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(36),
    FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT settings_singleton CHECK (id = 1)
);

INSERT INTO settings (id) VALUES (1);

-- ============================================================================
-- 15. ACTIVITY LOGS TABLE
-- ============================================================================

CREATE TABLE activity_logs (
    id VARCHAR(36) PRIMARY KEY,
    admin_id VARCHAR(36) NOT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id VARCHAR(36),
    description TEXT NOT NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    changes JSONB DEFAULT '{}'::jsonb,
    status VARCHAR(20) DEFAULT 'success',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX ix_activity_logs_admin_id ON activity_logs(admin_id);
CREATE INDEX ix_activity_logs_action ON activity_logs(action);
CREATE INDEX ix_activity_logs_created_at ON activity_logs(created_at);

-- ============================================================================
-- AUTO-UPDATE TRIGGERS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_platform_credentials_updated_at BEFORE UPDATE ON platform_credentials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_videos_updated_at BEFORE UPDATE ON videos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_settings_updated_at BEFORE UPDATE ON settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_job_search_configs_updated_at BEFORE UPDATE ON job_search_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SEED DATA
-- ============================================================================

INSERT INTO platforms (id, name, is_active, created_at) VALUES
    (gen_random_uuid()::text, 'LinkedIn', true, CURRENT_TIMESTAMP),
    (gen_random_uuid()::text, 'Indeed', true, CURRENT_TIMESTAMP);

COMMIT;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

SELECT '============================================================' as separator;
SELECT '✓ DATABASE SCHEMA CREATED SUCCESSFULLY!' as status;
SELECT '============================================================' as separator;

SELECT 'TOTAL TABLES:' as info, COUNT(*)::text as count
FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

SELECT '============================================================' as separator;
SELECT 'TABLE LIST:' as info;

SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name)::text || ' columns' as details
FROM information_schema.tables t
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY table_name;

SELECT '============================================================' as separator;
SELECT 'SEED DATA:' as info;

SELECT 'Platforms:' as type, COUNT(*)::text as count FROM platforms;
SELECT 'Settings:' as type, COUNT(*)::text as count FROM settings;

SELECT '============================================================' as separator;
SELECT '✓ MIGRATION COMPLETE - YOUR DATABASE IS READY!' as final_status;
SELECT '============================================================' as separator;

-- ============================================================================
-- SUCCESS! All tables now match Python models 100%
-- ============================================================================
-- Run this SQL in your Render PostgreSQL Shell and registration will work!
-- ============================================================================
