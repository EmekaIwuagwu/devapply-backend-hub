"""
N8N Integration Routes
Endpoints for n8n workflow automation (no JWT required)
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from app.models.resume import Resume
from app.models.application import Application
from app.models.platform_credential import PlatformCredential
from app.utils.responses import create_response, error_response
from app.utils.email_service import email_service
from datetime import datetime

n8n_bp = Blueprint('n8n', __name__)


@n8n_bp.route('/user-data', methods=['GET'])
def get_user_data():
    """
    Get user data for n8n workflows

    Query Parameters:
        email or user: User's email address

    Returns:
        - User profile (full_name, email, phone, location, etc.)
        - Default resume as base64
        - Platform credentials (LinkedIn URL, etc.)
        - Skills and preferences

    Example:
        GET /api/n8n/user-data?email=user@example.com
        GET /api/n8n/user-data?user=user@example.com
    """
    try:
        # Get email from query params (supports both 'email' and 'user')
        email = request.args.get('email') or request.args.get('user')

        if not email:
            return error_response(
                'MISSING_EMAIL',
                'Email parameter is required (?email=user@example.com)',
                status_code=400
            )

        # Find user by email
        user = User.query.filter_by(email=email).first()

        if not user:
            return error_response(
                'USER_NOT_FOUND',
                f'No user found with email: {email}',
                status_code=404
            )

        # Get default resume (or first resume if no default)
        resume = Resume.query.filter_by(user_id=user.id, is_default=True).first()
        if not resume:
            resume = Resume.query.filter_by(user_id=user.id).order_by(Resume.uploaded_at.desc()).first()

        # Get LinkedIn credentials if available
        linkedin_cred = PlatformCredential.query.filter_by(
            user_id=user.id,
            platform='linkedin'
        ).first()

        # Build response data
        user_data = {
            'user_id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'phone': user.phone,
            'location': user.location,
            'linkedin_url': user.linkedin_url,
            'github_url': user.github_url,
            'portfolio_url': user.portfolio_url,
            'current_role': user.current_role,
            'years_experience': user.years_experience,
            'preferred_job_type': user.preferred_job_type,
            'salary_expectations': user.salary_expectations,
            'professional_bio': user.professional_bio,
            'skills': user.skills or [],
            'linkedin_email': linkedin_cred.get_username() if linkedin_cred else None,
            'has_linkedin_credentials': bool(linkedin_cred),
            'has_linkedin_cookies': linkedin_cred.has_cookies() if linkedin_cred else False
        }

        # Add resume data if available
        if resume:
            user_data['resume'] = {
                'filename': resume.filename,
                'file_base64': resume.file_base64,
                'file_type': resume.file_type,
                'file_size': resume.file_size,
                'job_type_tag': resume.job_type_tag
            }
        else:
            user_data['resume'] = None

        return create_response(
            data=user_data,
            message='User data retrieved successfully'
        )

    except Exception as e:
        return error_response(
            'FETCH_ERROR',
            str(e),
            status_code=500
        )


@n8n_bp.route('/save-application', methods=['POST'])
def save_application():
    """
    Save job application and send email notification

    Request Body:
        {
            "email": "user@example.com",  // User's email (required)
            "company_name": "Company Inc",  // Required
            "job_title": "Software Engineer",  // Required
            "platform": "LinkedIn",  // Required (LinkedIn, Indeed, etc.)
            "job_url": "https://...",  // Optional
            "location": "Remote",  // Optional
            "job_type": "Full-time",  // Optional
            "salary_range": "$100k-$150k",  // Optional
            "status": "sent",  // Optional (default: sent)
            "cover_letter": "...",  // Optional
            "notes": "..."  // Optional
        }

    Returns:
        - Saved application data
        - Email notification status

    Example:
        POST /api/n8n/save-application
        {
            "email": "user@example.com",
            "company_name": "Google",
            "job_title": "Senior Software Engineer",
            "platform": "LinkedIn",
            "job_url": "https://linkedin.com/jobs/123"
        }
    """
    try:
        data = request.get_json()

        if not data:
            return error_response(
                'INVALID_REQUEST',
                'Request body is required',
                status_code=400
            )

        # Validate required fields
        email = data.get('email')
        company_name = data.get('company_name')
        job_title = data.get('job_title')
        platform = data.get('platform')

        if not email:
            return error_response('MISSING_FIELD', 'email is required', status_code=400)
        if not company_name:
            return error_response('MISSING_FIELD', 'company_name is required', status_code=400)
        if not job_title:
            return error_response('MISSING_FIELD', 'job_title is required', status_code=400)
        if not platform:
            return error_response('MISSING_FIELD', 'platform is required', status_code=400)

        # Find user by email
        user = User.query.filter_by(email=email).first()

        if not user:
            return error_response(
                'USER_NOT_FOUND',
                f'No user found with email: {email}',
                status_code=404
            )

        # Get default resume ID if available
        resume = Resume.query.filter_by(user_id=user.id, is_default=True).first()
        if not resume:
            resume = Resume.query.filter_by(user_id=user.id).order_by(Resume.uploaded_at.desc()).first()

        # Create application record
        application = Application(
            user_id=user.id,
            company_name=company_name,
            job_title=job_title,
            platform=platform,
            job_url=data.get('job_url'),
            location=data.get('location'),
            job_type=data.get('job_type'),
            salary_range=data.get('salary_range'),
            status=data.get('status', 'sent'),
            cover_letter=data.get('cover_letter'),
            notes=data.get('notes'),
            resume_used_id=resume.id if resume else None,
            applied_at=datetime.utcnow(),
            last_status_update=datetime.utcnow()
        )

        db.session.add(application)
        db.session.commit()

        # Send email notification
        email_sent = False
        try:
            email_data = {
                'company_name': company_name,
                'job_title': job_title,
                'platform': platform,
                'location': data.get('location') or 'Not specified',
                'status': application.status
            }

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #10b981; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background: #f9fafb; }}
                    .job-details {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                    .detail-row {{ margin: 10px 0; }}
                    .label {{ font-weight: bold; color: #6b7280; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>✅ New Application Submitted</h1>
                    </div>

                    <div class="content">
                        <p>Hi {user.full_name or 'there'},</p>

                        <p>Your job application has been successfully submitted!</p>

                        <div class="job-details">
                            <div class="detail-row">
                                <span class="label">Company:</span> {company_name}
                            </div>
                            <div class="detail-row">
                                <span class="label">Position:</span> {job_title}
                            </div>
                            <div class="detail-row">
                                <span class="label">Platform:</span> {platform}
                            </div>
                            <div class="detail-row">
                                <span class="label">Location:</span> {data.get('location') or 'Not specified'}
                            </div>
                            <div class="detail-row">
                                <span class="label">Status:</span> {application.status}
                            </div>
                            {f'<div class="detail-row"><span class="label">URL:</span> <a href="{data.get("job_url")}">{data.get("job_url")}</a></div>' if data.get('job_url') else ''}
                        </div>

                        <p>We'll keep you updated on any status changes.</p>

                        <p>Good luck! 🚀</p>
                    </div>
                </div>
            </body>
            </html>
            """

            email_sent = email_service.send_email(
                to=user.email,
                subject=f"Application Submitted: {company_name} - {job_title}",
                html_content=html_content
            )

        except Exception as email_error:
            print(f"[N8N] Email notification failed: {str(email_error)}")
            # Don't fail the whole request if email fails

        return create_response(
            data={
                'application': application.to_dict(),
                'email_sent': email_sent
            },
            message='Application saved successfully'
        ), 201

    except Exception as e:
        db.session.rollback()
        return error_response(
            'SAVE_ERROR',
            str(e),
            status_code=500
        )
