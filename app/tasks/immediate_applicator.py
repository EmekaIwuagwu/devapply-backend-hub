"""
Immediate job application task - starts applying as soon as config is saved
"""
from datetime import datetime
from app.celery_config import celery
from app import db
from app.models.user import User
from app.models.job_search_config import JobSearchConfig
from app.models.resume import Resume
from app.models.application import Application
from app.models.subscription import Subscription
from app.models.automation_log import AutomationLog
from app.models.platform_credential import PlatformCredential


@celery.task(name='app.tasks.immediate_applicator.start_immediate_applications')
def start_immediate_applications(user_id, config_id):
    """
    Start applying to jobs IMMEDIATELY when config is saved
    Applies to ALL matching jobs on configured platforms
    Processes both primary and secondary configs simultaneously
    """
    try:
        # Log task started to console
        print("=" * 80)
        print(f"IMMEDIATE APPLICATION TASK STARTED")
        print(f"User ID: {user_id}, Config ID: {config_id}")
        print("=" * 80)

        # Log start
        log_event(user_id, 'immediate_apply_start', 'info',
                 f'Starting immediate job applications for user {user_id}')

        user = User.query.get(user_id)
        if not user:
            log_event(user_id, 'immediate_apply', 'failed', 'User not found')
            return {"success": False, "error": "User not found"}

        config = JobSearchConfig.query.get(config_id)
        if not config:
            log_event(user_id, 'immediate_apply', 'failed', 'Config not found')
            return {"success": False, "error": "Config not found"}

        # Check subscription limits
        subscription = Subscription.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()

        if subscription and subscription.applications_used >= subscription.applications_limit:
            log_event(user_id, 'immediate_apply', 'failed',
                     f'Application limit reached: {subscription.applications_used}/{subscription.applications_limit}')
            return {"success": False, "error": "Application limit reached"}

        # Get platform credentials
        platforms = config.platforms or []
        if not platforms:
            log_event(user_id, 'immediate_apply', 'failed', 'No platforms configured')
            return {"success": False, "error": "No platforms configured"}

        log_event(user_id, 'config_loaded', 'info',
                 f'Loaded config with {len(platforms)} platform(s): {", ".join(platforms)}')

        # Get user's resumes
        resumes = Resume.query.filter_by(user_id=user_id).all()
        if not resumes:
            log_event(user_id, 'immediate_apply', 'failed', 'No resumes uploaded')
            return {"success": False, "error": "No resumes uploaded"}

        log_event(user_id, 'resumes_found', 'info',
                 f'Found {len(resumes)} resume(s) in database')

        total_applied = 0
        errors = []

        # Apply to both PRIMARY and SECONDARY configs simultaneously
        configs_to_process = []

        # Add primary config
        if config.primary_job_title:
            configs_to_process.append({
                'type': 'primary',
                'job_title': config.primary_job_title,
                'location': config.primary_location,
                'job_type': config.primary_job_type,
                'min_salary': config.primary_min_salary,
                'max_salary': config.primary_max_salary,
                'experience_level': config.primary_experience_level,
                'remote_preference': config.primary_remote_preference,
                'keywords': config.primary_keywords or [],
                'resume_id': config.primary_resume_id
            })
            log_event(user_id, 'primary_config_loaded', 'info',
                     f'Primary search: {config.primary_job_title} in {config.primary_location or "Any location"}')

        # Add secondary config
        if config.secondary_job_title:
            configs_to_process.append({
                'type': 'secondary',
                'job_title': config.secondary_job_title,
                'location': config.secondary_location,
                'job_type': config.secondary_job_type,
                'min_salary': config.secondary_min_salary,
                'max_salary': config.secondary_max_salary,
                'experience_level': config.secondary_experience_level,
                'remote_preference': config.secondary_remote_preference,
                'keywords': config.secondary_keywords or [],
                'resume_id': config.secondary_resume_id
            })
            log_event(user_id, 'secondary_config_loaded', 'info',
                     f'Secondary search: {config.secondary_job_title} in {config.secondary_location or "Any location"}')

        # Process each config
        for search_config in configs_to_process:
            config_type = search_config['type']

            # Get appropriate resume
            resume = get_matching_resume(resumes, search_config)
            if not resume:
                error_msg = f"No matching resume for {config_type} config"
                log_event(user_id, 'resume_match_failed', 'failed', error_msg)
                errors.append(error_msg)
                continue

            log_event(user_id, 'resume_matched', 'success',
                     f'{config_type.capitalize()} config matched to resume: {resume.filename}')

            # Process each platform
            for platform in platforms:
                try:
                    # Get platform credentials
                    credential = PlatformCredential.query.filter_by(
                        user_id=user_id,
                        platform=platform.lower()
                    ).first()

                    if not credential:
                        error_msg = f"No credentials for {platform}"
                        log_event(user_id, 'credentials_missing', 'failed',
                                f'{error_msg} - Please add credentials on Credentials page')
                        errors.append(error_msg)
                        continue

                    log_event(user_id, 'credentials_found', 'success',
                             f'{platform} credentials found for {config_type} config')

                    # Search and apply to jobs on this platform
                    applied_count = search_and_apply_immediate(
                        user=user,
                        config=config,
                        search_config=search_config,
                        platform=platform,
                        credential=credential,
                        resume=resume,
                        subscription=subscription
                    )

                    total_applied += applied_count
                    log_event(user_id, 'platform_complete', 'success',
                             f'Applied to {applied_count} job(s) on {platform} for {config_type} search')

                except Exception as e:
                    error_msg = f"Error on {platform}: {str(e)}"
                    log_event(user_id, 'platform_error', 'failed', error_msg)
                    errors.append(error_msg)

        # Log completion
        log_event(
            user_id,
            'immediate_apply_complete',
            'success',
            f"✅ Job application process complete! Applied to {total_applied} total job(s)",
            details={
                'total_applied': total_applied,
                'platforms': platforms,
                'configs_processed': len(configs_to_process),
                'errors': errors if errors else None
            }
        )

        return {
            "success": True,
            "total_applied": total_applied,
            "errors": errors
        }

    except Exception as e:
        log_event(user_id, 'immediate_apply', 'failed', f"Fatal error: {str(e)}")
        return {"success": False, "error": str(e)}


def get_matching_resume(resumes, search_config):
    """
    Get resume that matches the job search config
    Matches based on resume filename or job_type_tag
    """
    job_title = search_config['job_title'].lower()
    resume_id = search_config.get('resume_id')

    # First, try to use specified resume
    if resume_id:
        for resume in resumes:
            if resume.id == resume_id:
                return resume

    # Match by filename or job_type_tag
    for resume in resumes:
        filename = (resume.filename or '').lower()
        job_tag = (resume.job_type_tag or '').lower()

        # Check if job title keywords are in resume name/tag
        job_keywords = job_title.split()
        for keyword in job_keywords:
            if len(keyword) > 3:  # Only meaningful keywords
                if keyword in filename or keyword in job_tag:
                    return resume

    # Fall back to default resume
    for resume in resumes:
        if resume.is_default:
            return resume

    # Return first resume if no match
    return resumes[0] if resumes else None


def search_and_apply_immediate(user, config, search_config, platform, credential, resume, subscription):
    """
    Search for jobs and apply IMMEDIATELY (no queue)
    Applies to ALL matching jobs found
    """
    from app.automation.linkedin_bot import LinkedInBot
    from app.automation.indeed_bot import IndeedBot

    applied_count = 0
    config_type = search_config['type']

    try:
        # Log platform start
        log_event(user.id, 'platform_start', 'info',
                 f'🚀 Starting {platform} automation for {config_type} search')

        # Prepare user profile with credentials
        user_profile = user.to_dict()

        if platform.lower() == 'linkedin':
            user_profile['linkedin_email'] = credential.get_username()
            user_profile['linkedin_password'] = credential.get_password()

            log_event(user.id, 'credentials_loaded', 'info',
                     f'LinkedIn credentials loaded for user')

            bot = LinkedInBot(user_profile=user_profile, resume_base64=resume.file_base64)
        elif platform.lower() == 'indeed':
            user_profile['indeed_email'] = credential.get_username()
            user_profile['indeed_password'] = credential.get_password()
            bot = IndeedBot(user_profile=user_profile, resume_base64=resume.file_base64)
        else:
            log_event(user.id, 'platform_unsupported', 'failed',
                     f'No automation bot available for {platform}')
            return 0

        # Initialize browser BEFORE login
        log_event(user.id, 'browser_init', 'info',
                 f'Initializing browser for {platform}...')

        try:
            bot.initialize_browser()
        except Exception as e:
            log_event(user.id, 'browser_init', 'failed',
                     f'Failed to initialize browser: {str(e)}')
            return 0

        # Login to platform
        log_event(user.id, 'platform_login_attempt', 'info',
                 f'🔐 Logging into {platform}...')

        if not bot.login():
            log_event(user.id, 'platform_login', 'failed',
                     f"❌ Failed to login to {platform} - Please check your credentials")
            return 0

        log_event(user.id, 'platform_login', 'success',
                 f'✅ Successfully logged into {platform}!')

        # Search for jobs
        log_event(user.id, 'job_search_start', 'info',
                 f'🔍 Searching for {search_config["job_title"]} jobs on {platform}...',
                 details={
                     'job_title': search_config['job_title'],
                     'location': search_config['location'],
                     'job_type': search_config['job_type'],
                     'experience_level': search_config['experience_level']
                 })

        jobs = bot.search_jobs(
            job_title=search_config['job_title'],
            location=search_config['location'],
            job_type=search_config['job_type'],
            experience_level=search_config['experience_level'],
            remote_preference=search_config['remote_preference'],
            keywords=search_config['keywords']
        )

        jobs_count = len(jobs)
        log_event(user.id, 'job_search_complete', 'success',
                 f'📋 Found {jobs_count} matching job(s) on {platform}',
                 details={'jobs_found': jobs_count})

        if jobs_count == 0:
            log_event(user.id, 'no_jobs_found', 'info',
                     f'No matching jobs found for {search_config["job_title"]} on {platform}')
            bot.logout()
            return 0

        # Apply to ALL matching jobs
        log_event(user.id, 'application_start', 'info',
                 f'📝 Starting to apply to {jobs_count} job(s)...')

        for idx, job in enumerate(jobs, 1):
            try:
                # Check if already applied
                existing = Application.query.filter_by(
                    user_id=user.id,
                    job_url=job['job_url']
                ).first()

                if existing:
                    log_event(user.id, 'job_skipped', 'info',
                             f'⏭️ Skipped {job["company_name"]} - Already applied')
                    continue

                # Check subscription limit
                if subscription and subscription.applications_used >= subscription.applications_limit:
                    log_event(user.id, 'application_limit_reached', 'info',
                             f'🛑 Application limit reached ({subscription.applications_limit}). Stopping.')
                    break

                # Apply to job
                log_event(user.id, 'job_application_attempt', 'info',
                         f'📤 Applying to job {idx}/{jobs_count}: {job["company_name"]} - {job["job_title"]}')

                success, message = bot.apply_to_job(job['job_url'])

                if success:
                    # Create application record
                    application = Application(
                        user_id=user.id,
                        company_name=job['company_name'],
                        job_title=job['job_title'],
                        job_type=job.get('job_type'),
                        location=job.get('location'),
                        salary_range=job.get('salary_range'),
                        platform=platform,
                        job_url=job['job_url'],
                        status='sent',
                        resume_used_id=resume.id,
                        applied_at=datetime.utcnow()
                    )
                    db.session.add(application)

                    # Update subscription usage
                    if subscription:
                        subscription.applications_used += 1

                    # Update resume last used
                    resume.last_used_at = datetime.utcnow()

                    applied_count += 1
                    db.session.commit()

                    # Log success
                    log_event(
                        user.id,
                        'job_apply',
                        'success',
                        f"✅ Successfully applied to {job['company_name']} - {job['job_title']}",
                        details={
                            'platform': platform,
                            'config_type': config_type,
                            'company': job['company_name'],
                            'job_title': job['job_title'],
                            'location': job.get('location'),
                            'total_applied': applied_count
                        }
                    )
                else:
                    # Log failure
                    log_event(user.id, 'job_apply', 'failed',
                             f"❌ Failed to apply to {job['company_name']}: {message}")

            except Exception as e:
                log_event(user.id, 'job_apply_error', 'failed',
                         f"⚠️ Error applying to {job.get('company_name', 'Unknown')}: {str(e)}")
                continue

        # Logout
        log_event(user.id, 'platform_logout', 'info',
                 f'🔓 Logging out of {platform}')
        try:
            bot.logout()
        except:
            pass  # Logout errors are not critical

        log_event(user.id, 'platform_session_complete', 'success',
                 f'✅ {platform} session complete: Applied to {applied_count}/{jobs_count} job(s)')

        return applied_count

    except Exception as e:
        log_event(user.id, 'platform_error', 'failed',
                 f"❌ Error in {platform} automation: {str(e)}")
        return applied_count

    finally:
        # Always cleanup browser resources
        try:
            if 'bot' in locals() and bot:
                bot.cleanup()
        except:
            pass  # Cleanup errors are not critical


def log_event(user_id, action_type, status, message, details=None):
    """Log automation event"""
    try:
        log = AutomationLog(
            user_id=user_id,
            action_type=action_type,
            status=status,
            message=message,
            details=details or {}
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Error logging event: {str(e)}")
