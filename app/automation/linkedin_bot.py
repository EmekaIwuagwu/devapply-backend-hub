"""
LinkedIn Easy Apply automation bot
"""
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from app.automation.bot_base import JobApplicationBot


class LinkedInBot(JobApplicationBot):
    """
    Automated job application bot for LinkedIn Easy Apply
    """

    def initialize_browser(self):
        """Initialize Selenium WebDriver"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # Set Chrome binary location (required on some systems)
        options.binary_location = '/usr/bin/google-chrome-stable'

        # User agent
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 15)

        return self.driver

    def login(self):
        """
        Login to LinkedIn
        Requires credentials to be passed in user profile
        """
        try:
            print("[LinkedIn Bot] Logging in...")

            # Navigate to login page
            self.driver.get('https://www.linkedin.com/login')
            time.sleep(2)

            # Get credentials from user profile
            username = self.user.get('linkedin_email')
            password = self.user.get('linkedin_password')

            if not username or not password:
                print("[LinkedIn Bot] No credentials found")
                return False

            # Enter username
            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, 'username'))
            )
            username_field.clear()
            username_field.send_keys(username)

            # Enter password
            password_field = self.driver.find_element(By.ID, 'password')
            password_field.clear()
            password_field.send_keys(password)

            # Click login button
            login_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
            login_button.click()

            # Wait for redirect to feed
            time.sleep(5)

            # Check if login successful
            if '/feed' in self.driver.current_url or '/mynetwork' in self.driver.current_url:
                print("[LinkedIn Bot] Login successful")
                return True
            else:
                print("[LinkedIn Bot] Login failed - unexpected URL")
                return False

        except Exception as e:
            print(f"[LinkedIn Bot] Login error: {str(e)}")
            return False

    def navigate_to_job(self, job_url):
        """Navigate to job posting"""
        try:
            print(f"[LinkedIn Bot] Navigating to job: {job_url}")
            self.driver.get(job_url)
            time.sleep(3)

            # Check if Easy Apply button exists
            try:
                easy_apply_button = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.jobs-apply-button'))
                )
                return True
            except TimeoutException:
                print("[LinkedIn Bot] Easy Apply button not found")
                return False

        except Exception as e:
            print(f"[LinkedIn Bot] Navigation error: {str(e)}")
            return False

    def fill_application_form(self):
        """
        Fill LinkedIn Easy Apply form
        Handles multi-step forms
        """
        try:
            print("[LinkedIn Bot] Filling application form...")

            # Click Easy Apply button
            easy_apply_button = self.driver.find_element(By.CSS_SELECTOR, '.jobs-apply-button')
            easy_apply_button.click()
            time.sleep(2)

            # Handle multi-step form
            max_steps = 10
            current_step = 0

            while current_step < max_steps:
                print(f"[LinkedIn Bot] Processing step {current_step + 1}...")

                # Fill current page
                if not self._fill_current_page():
                    print("[LinkedIn Bot] Error filling current page")
                    return False

                # Check if there's a Next button
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Continue to next step"]')
                    if next_button.is_enabled():
                        next_button.click()
                        time.sleep(2)
                        current_step += 1
                    else:
                        break
                except NoSuchElementException:
                    # No next button, must be final step
                    break

            print("[LinkedIn Bot] Form filled successfully")
            return True

        except Exception as e:
            print(f"[LinkedIn Bot] Form filling error: {str(e)}")
            return False

    def _fill_current_page(self):
        """Fill fields on current page"""
        try:
            # Find all input fields
            inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"], input[type="tel"], input[type="email"]')

            for input_field in inputs:
                try:
                    # Get field label
                    field_id = input_field.get_attribute('id')
                    field_name = input_field.get_attribute('name')

                    # Skip if already filled
                    if input_field.get_attribute('value'):
                        continue

                    # Map fields to user data
                    if 'phone' in field_name.lower() or 'mobile' in field_name.lower():
                        if self.user.get('phone'):
                            input_field.send_keys(self.user['phone'])

                    elif 'email' in field_name.lower():
                        if self.user.get('email'):
                            input_field.send_keys(self.user['email'])

                    elif 'city' in field_name.lower() or 'location' in field_name.lower():
                        if self.user.get('location'):
                            input_field.send_keys(self.user['location'])

                except Exception as e:
                    print(f"[LinkedIn Bot] Error filling field: {str(e)}")
                    continue

            # Handle dropdowns/select fields
            selects = self.driver.find_elements(By.CSS_SELECTOR, 'select')
            for select in selects:
                try:
                    # For now, select first non-empty option
                    options = select.find_elements(By.TAG_NAME, 'option')
                    if len(options) > 1:
                        options[1].click()
                except:
                    pass

            # Handle radio buttons (usually yes/no questions)
            # Default to "No" for questions about sponsorship, relocation, etc.
            radio_groups = self.driver.find_elements(By.CSS_SELECTOR, 'fieldset')
            for group in radio_groups:
                try:
                    radios = group.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')
                    if radios:
                        # Click first radio (usually "No")
                        radios[0].click()
                except:
                    pass

            return True

        except Exception as e:
            print(f"[LinkedIn Bot] Error in _fill_current_page: {str(e)}")
            return False

    def upload_resume(self):
        """Upload resume to application"""
        try:
            print("[LinkedIn Bot] Looking for resume upload...")

            # Look for file upload input
            try:
                file_input = self.driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')

                # Save resume to temp file
                resume_path = self.save_resume_to_file()

                # Upload file
                file_input.send_keys(resume_path)
                time.sleep(2)

                print("[LinkedIn Bot] Resume uploaded")
                return True

            except NoSuchElementException:
                # Resume upload might not be required
                print("[LinkedIn Bot] No resume upload field found (might not be required)")
                return True

        except Exception as e:
            print(f"[LinkedIn Bot] Resume upload error: {str(e)}")
            return True  # Don't fail application if resume upload fails

    def submit_application(self):
        """Submit the application"""
        try:
            print("[LinkedIn Bot] Submitting application...")

            # Look for submit button
            submit_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Submit application"]'))
            )

            submit_button.click()
            time.sleep(3)

            # Check for confirmation
            try:
                confirmation = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.artdeco-modal__header'))
                )
                if 'application sent' in confirmation.text.lower() or 'submitted' in confirmation.text.lower():
                    print("[LinkedIn Bot] Application submitted successfully")
                    return True
            except TimeoutException:
                pass

            # Alternative check - look for success message
            try:
                success_msg = self.driver.find_element(By.CSS_SELECTOR, '.artdeco-inline-feedback--success')
                if success_msg:
                    print("[LinkedIn Bot] Application submitted successfully")
                    return True
            except NoSuchElementException:
                pass

            print("[LinkedIn Bot] Application submitted (confirmation not found but no error)")
            return True

        except Exception as e:
            print(f"[LinkedIn Bot] Submission error: {str(e)}")
            return False

    def check_if_already_applied(self, job_url):
        """Check if user already applied to this job"""
        try:
            self.driver.get(job_url)
            time.sleep(2)

            # Look for "Applied" indicator
            try:
                applied_indicator = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Applied')]")
                if applied_indicator:
                    print("[LinkedIn Bot] Already applied to this job")
                    return True
            except NoSuchElementException:
                pass

            return False

        except Exception as e:
            print(f"[LinkedIn Bot] Error checking application status: {str(e)}")
            return False
