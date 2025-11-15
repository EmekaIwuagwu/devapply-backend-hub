"""
Job scraper tasks for discovering jobs across platforms
"""
from datetime import datetime, timedelta
from app.celery_config import celery
from app import db
from app.models.user import User
from app.models.job_search_config import JobSearchConfig
from app.models.job_listing import JobListing
from app.models.job_queue import JobQueue
from app.models.automation_log import AutomationLog
from app.utils.job_matcher import calculate_match_score, should_apply_to_job


@celery.task(name='app.tasks.job_scraper.scrape_jobs_all_users')
def scrape_jobs_all_users():
    """
    Scrape jobs for all active users
    Runs every 6 hours via Celery Beat
    """
    # Get all users with active job search configs
    users = User.query.join(JobSearchConfig).filter(
        JobSearchConfig.is_active == True
    ).all()

    for user in users:
        try:
            scrape_jobs_for_user.delay(user.id)
        except Exception as e:
            print(f"Error queuing scrape for user {user.id}: {str(e)}")

    return f"Queued scraping for {len(users)} users"


@celery.task(name='app.tasks.job_scraper.scrape_jobs_for_user')
def scrape_jobs_for_user(user_id):
    """
    Scrape jobs from configured platforms for a specific user
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return f"User {user_id} not found"

        config = JobSearchConfig.query.filter_by(user_id=user_id, is_active=True).first()
        if not config:
            return f"No active job search config for user {user_id}"

        # Get configured platforms
        platforms = config.platforms or []
        if not platforms:
            return f"No platforms configured for user {user_id}"

        total_jobs_found = 0
        total_queued = 0

        # Scrape each platform
        for platform in platforms:
            try:
                # Call platform-specific scraper
                jobs = scrape_platform(platform, config)

                for job_data in jobs:
                    # Create or update job listing
                    job_listing = create_or_update_job_listing(job_data)

                    if job_listing:
                        total_jobs_found += 1

                        # Calculate match score
                        match_score = calculate_match_score(
                            job_listing,
                            config,
                            user.skills or []
                        )

                        # If match score is good, add to queue
                        should_apply, score, reasons = should_apply_to_job(
                            job_listing,
                            config,
                            user.skills or [],
                            threshold=70.0
                        )

                        if should_apply:
                            # Check if already queued or applied
                            existing_queue = JobQueue.query.filter_by(
                                user_id=user_id,
                                job_listing_id=job_listing.id
                            ).first()

                            existing_app = db.session.query(db.exists().where(
                                db.and_(
                                    db.column('user_id') == user_id,
                                    db.column('job_url') == job_listing.job_url
                                )
                            )).scalar()

                            if not existing_queue and not existing_app:
                                # Add to queue
                                queue_item = JobQueue(
                                    user_id=user_id,
                                    job_search_config_id=config.id,
                                    platform=platform,
                                    job_listing_id=job_listing.id,
                                    company_name=job_listing.company_name,
                                    job_title=job_listing.job_title,
                                    job_url=job_listing.job_url,
                                    status='pending',
                                    priority=calculate_priority(match_score),
                                    match_score=match_score,
                                    scheduled_for=datetime.utcnow()
                                )
                                db.session.add(queue_item)
                                total_queued += 1

            except Exception as e:
                log_automation_event(
                    user_id=user_id,
                    action_type='job_search',
                    status='failed',
                    message=f"Error scraping {platform}: {str(e)}"
                )

        db.session.commit()

        # Log success
        log_automation_event(
            user_id=user_id,
            action_type='job_search',
            status='success',
            message=f"Found {total_jobs_found} jobs, queued {total_queued} for application",
            details={'platforms': platforms}
        )

        return f"Scraped {total_jobs_found} jobs, queued {total_queued} for user {user_id}"

    except Exception as e:
        db.session.rollback()
        log_automation_event(
            user_id=user_id,
            action_type='job_search',
            status='failed',
            message=f"Scraping failed: {str(e)}"
        )
        return f"Error: {str(e)}"


def scrape_platform(platform, config):
    """
    Scrape jobs from a specific platform using real scrapers
    """
    import os
    from app.scrapers.linkedin_scraper import LinkedInScraper
    from app.scrapers.indeed_scraper import IndeedScraper

    try:
        proxy_url = os.getenv('PROXY_SERVICE_URL')
        proxy_key = os.getenv('PROXY_SERVICE_KEY')

        platform_lower = platform.lower()

        if platform_lower == 'linkedin':
            scraper = LinkedInScraper(proxy_url, proxy_key)
            return scraper.scrape(
                job_title=config.primary_job_title or '',
                location=config.primary_location or '',
                keywords=config.primary_keywords or []
            )

        elif platform_lower == 'indeed':
            scraper = IndeedScraper(proxy_url, proxy_key)
            return scraper.scrape(
                job_title=config.primary_job_title or '',
                location=config.primary_location or '',
                keywords=config.primary_keywords or []
            )

        else:
            print(f"No scraper implemented for platform: {platform}")
            return []

    except Exception as e:
        print(f"Error scraping {platform}: {str(e)}")
        return []


def create_or_update_job_listing(job_data):
    """Create or update job listing in database"""
    try:
        # Check if job already exists
        existing = JobListing.query.filter_by(
            platform=job_data['platform'],
            external_id=job_data['external_id']
        ).first()

        if existing:
            # Update existing listing
            existing.scraped_at = datetime.utcnow()
            existing.is_active = True
            return existing
        else:
            # Create new listing
            job_listing = JobListing(
                platform=job_data['platform'],
                external_id=job_data['external_id'],
                company_name=job_data['company_name'],
                job_title=job_data['job_title'],
                location=job_data.get('location'),
                salary_range=job_data.get('salary_range'),
                job_type=job_data.get('job_type'),
                description=job_data.get('description'),
                requirements=job_data.get('requirements'),
                job_url=job_data['job_url'],
                posted_date=job_data.get('posted_date'),
                is_active=True
            )
            db.session.add(job_listing)
            return job_listing

    except Exception as e:
        print(f"Error creating job listing: {str(e)}")
        return None


def calculate_priority(match_score):
    """Calculate priority (1-10) based on match score"""
    if match_score >= 90:
        return 10
    elif match_score >= 80:
        return 8
    elif match_score >= 70:
        return 6
    else:
        return 5


def log_automation_event(user_id, action_type, status, message, details=None, job_queue_id=None):
    """Log automation event"""
    try:
        log = AutomationLog(
            user_id=user_id,
            job_queue_id=job_queue_id,
            action_type=action_type,
            status=status,
            message=message,
            details=details or {}
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Error logging automation event: {str(e)}")
