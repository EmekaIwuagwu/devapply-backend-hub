"""
Email notification service
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template


class EmailService:
    """Service for sending transactional emails"""

    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_pass = os.getenv('SMTP_PASS')
        self.from_email = os.getenv('SMTP_FROM', 'noreply@devapply.com')

    def send_email(self, to, subject, html_content, text_content=None):
        """
        Send email using SMTP

        Args:
            to (str): Recipient email
            subject (str): Email subject
            html_content (str): HTML body
            text_content (str): Plain text body (optional)

        Returns:
            bool: Success status
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to

            # Add text version if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)

            # Add HTML version
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Connect to SMTP server
            if not self.smtp_user or not self.smtp_pass:
                print(f"[Email] SMTP credentials not configured. Would send to {to}: {subject}")
                return True  # Simulate success in dev

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)

            print(f"[Email] Sent to {to}: {subject}")
            return True

        except Exception as e:
            print(f"[Email] Error sending email: {str(e)}")
            return False

    def send_daily_summary(self, user_email, data):
        """Send daily summary email"""
        subject = f"DevApply Daily Summary - {data['applications_submitted']} Applications"

        html_content = self._render_template('daily_summary', data)
        text_content = self._render_text_summary(data)

        return self.send_email(user_email, subject, html_content, text_content)

    def send_status_update(self, user_email, application_data):
        """Send application status update email"""
        subject = f"Application Update: {application_data['company_name']}"

        html_content = self._render_template('status_update', application_data)

        return self.send_email(user_email, subject, html_content)

    def send_welcome_email(self, user_email, user_name):
        """Send welcome email to new users"""
        subject = "Welcome to DevApply - Start Automating Your Job Search"

        data = {'user_name': user_name}
        html_content = self._render_template('welcome', data)

        return self.send_email(user_email, subject, html_content)

    def send_application_limit_warning(self, user_email, subscription_data):
        """Send warning when approaching application limit"""
        subject = "DevApply - Application Limit Warning"

        html_content = self._render_template('application_limit', subscription_data)

        return self.send_email(user_email, subject, html_content)

    def _render_template(self, template_name, data):
        """Render email template"""
        # Template mapping
        templates = {
            'daily_summary': DAILY_SUMMARY_TEMPLATE,
            'status_update': STATUS_UPDATE_TEMPLATE,
            'welcome': WELCOME_TEMPLATE,
            'application_limit': APPLICATION_LIMIT_TEMPLATE
        }

        template_str = templates.get(template_name, '')
        template = Template(template_str)

        return template.render(**data)

    def _render_text_summary(self, data):
        """Render plain text summary"""
        return f"""
DevApply Daily Summary

Applications Submitted: {data['applications_submitted']}
Pending Applications: {data['pending_applications']}
Status Updates: {data['status_updates']}

Visit DevApply to see more details.
        """.strip()


# Email Templates (HTML)

DAILY_SUMMARY_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #2563eb; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9fafb; }
        .stats { display: flex; justify-content: space-around; margin: 20px 0; }
        .stat { text-align: center; padding: 15px; background: white; border-radius: 8px; }
        .stat-number { font-size: 32px; font-weight: bold; color: #2563eb; }
        .stat-label { font-size: 14px; color: #6b7280; }
        .applications { margin: 20px 0; }
        .application { background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #2563eb; }
        .footer { text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Your Daily DevApply Summary</h1>
        </div>

        <div class="content">
            <h2>Yesterday's Activity</h2>

            <div class="stats">
                <div class="stat">
                    <div class="stat-number">{{ applications_submitted }}</div>
                    <div class="stat-label">Applications Sent</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{{ pending_applications }}</div>
                    <div class="stat-label">In Queue</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{{ status_updates }}</div>
                    <div class="stat-label">Status Updates</div>
                </div>
            </div>

            {% if applications %}
            <h3>Recent Applications</h3>
            <div class="applications">
                {% for app in applications %}
                <div class="application">
                    <strong>{{ app.company_name }}</strong> - {{ app.job_title }}<br>
                    <small>{{ app.platform }} • {{ app.location }}</small>
                </div>
                {% endfor %}
            </div>
            {% endif %}

            {% if updates %}
            <h3>Status Updates</h3>
            <div class="applications">
                {% for update in updates %}
                <div class="application">
                    <strong>{{ update.company_name }}</strong><br>
                    Status changed to: <strong>{{ update.status }}</strong>
                </div>
                {% endfor %}
            </div>
            {% endif %}
        </div>

        <div class="footer">
            <p>DevApply - Automated Job Applications</p>
            <p><a href="#">Unsubscribe</a></p>
        </div>
    </div>
</body>
</html>
"""

STATUS_UPDATE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #10b981; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9fafb; }
        .status-badge { display: inline-block; padding: 5px 15px; border-radius: 20px; background: #10b981; color: white; }
        .job-details { background: white; padding: 20px; margin: 20px 0; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Application Update!</h1>
        </div>

        <div class="content">
            <div class="job-details">
                <h2>{{ company_name }}</h2>
                <h3>{{ job_title }}</h3>
                <p><strong>Platform:</strong> {{ platform }}</p>
                <p><strong>Location:</strong> {{ location }}</p>
                <p><strong>New Status:</strong> <span class="status-badge">{{ status }}</span></p>
            </div>

            <p>Your application status has been updated. Log in to DevApply to see more details.</p>
        </div>
    </div>
</body>
</html>
"""

WELCOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #2563eb; color: white; padding: 30px; text-align: center; }
        .content { padding: 30px; background: #f9fafb; }
        .cta-button { display: inline-block; padding: 12px 30px; background: #2563eb; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to DevApply!</h1>
        </div>

        <div class="content">
            <h2>Hi {{ user_name }},</h2>

            <p>Welcome to DevApply - your AI-powered job application assistant!</p>

            <p>We're excited to help you automate your job search. Here's what you can do:</p>

            <ul>
                <li>📝 Upload your resumes</li>
                <li>🎯 Configure your job search preferences</li>
                <li>🤖 Let AI find and apply to jobs for you</li>
                <li>📊 Track all your applications in one place</li>
            </ul>

            <p><a href="#" class="cta-button">Get Started</a></p>

            <p>If you have any questions, feel free to reach out to our support team.</p>

            <p>Happy job hunting!</p>
        </div>
    </div>
</body>
</html>
"""

APPLICATION_LIMIT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #f59e0b; color: white; padding: 20px; text-align: center; }
        .content { padding: 20px; background: #f9fafb; }
        .upgrade-button { display: inline-block; padding: 12px 30px; background: #2563eb; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚠️ Application Limit Warning</h1>
        </div>

        <div class="content">
            <p>You've used <strong>{{ applications_used }}</strong> out of <strong>{{ applications_limit }}</strong> applications for your <strong>{{ plan_type }}</strong> plan.</p>

            <p>To continue applying to jobs automatically, consider upgrading your plan.</p>

            <p><a href="#" class="upgrade-button">Upgrade Plan</a></p>
        </div>
    </div>
</body>
</html>
"""

# Create singleton instance
email_service = EmailService()
