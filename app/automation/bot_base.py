"""
Base class for job application bots
"""
import base64
import os
import tempfile
from abc import ABC, abstractmethod


class JobApplicationBot(ABC):
    """
    Base class for platform-specific job application bots

    Each platform (LinkedIn, Indeed, etc.) should extend this class
    and implement the platform-specific methods.
    """

    def __init__(self, user_profile, resume_base64):
        """
        Initialize the bot

        Args:
            user_profile (dict): User profile data
            resume_base64 (str): Resume file in base64 format
        """
        self.user = user_profile
        self.resume_base64 = resume_base64
        self.driver = None

    @abstractmethod
    def initialize_browser(self):
        """
        Initialize headless browser (Selenium/Playwright)

        Returns:
            WebDriver instance
        """
        pass

    @abstractmethod
    def login(self):
        """
        Login to the platform

        Returns:
            bool: True if successful, False otherwise
        """
        pass

    @abstractmethod
    def navigate_to_job(self, job_url):
        """
        Navigate to job posting

        Args:
            job_url (str): URL of the job posting

        Returns:
            bool: True if successful
        """
        pass

    @abstractmethod
    def fill_application_form(self):
        """
        Fill out the application form

        Returns:
            bool: True if successful
        """
        pass

    @abstractmethod
    def upload_resume(self):
        """
        Upload resume to application

        Returns:
            bool: True if successful
        """
        pass

    @abstractmethod
    def submit_application(self):
        """
        Submit the application

        Returns:
            bool: True if successful
        """
        pass

    def save_resume_to_file(self):
        """
        Save base64 resume to temporary file

        Returns:
            str: Path to temporary file
        """
        # Decode base64
        resume_data = base64.b64decode(self.resume_base64)

        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.write(resume_data)
        temp_file.close()

        return temp_file.name

    def cleanup(self):
        """Clean up browser and temporary files"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

    def apply_to_job(self, job_url):
        """
        Main method to apply to a job

        Args:
            job_url (str): URL of job posting

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Initialize browser
            self.initialize_browser()

            # Login to platform
            if not self.login():
                return False, "Failed to login"

            # Navigate to job
            if not self.navigate_to_job(job_url):
                return False, "Failed to navigate to job"

            # Fill application form
            if not self.fill_application_form():
                return False, "Failed to fill application form"

            # Upload resume
            if not self.upload_resume():
                return False, "Failed to upload resume"

            # Submit application
            if not self.submit_application():
                return False, "Failed to submit application"

            return True, "Application submitted successfully"

        except Exception as e:
            return False, f"Error applying to job: {str(e)}"

        finally:
            self.cleanup()
