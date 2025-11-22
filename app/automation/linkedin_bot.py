"""
LinkedIn Easy Apply automation bot
"""
import time
import os
import undetected_chromedriver as uc
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
        """Initialize Selenium WebDriver with undetected-chromedriver"""
        options = uc.ChromeOptions()

        # Headless mode configuration
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')

        # Set Chrome binary location
        options.binary_location = '/usr/bin/google-chrome-stable'

        # Initialize undetected Chrome
        # version_main should match your Chrome version (142)
        self.driver = uc.Chrome(
            options=options,
            version_main=142,
            driver_executable_path=None,  # Auto-download matching chromedriver
            use_subprocess=False
        )

        # Set page load timeout to prevent hanging
        self.driver.set_page_load_timeout(45)

        self.driver.implicitly_wait(5)
        self.wait = WebDriverWait(self.driver, 20)

        print("[LinkedIn Bot] ✅ Undetected browser initialized successfully")
        return self.driver

    def login(self):
        """
        Login to LinkedIn
        Uses cookies if available, falls back to username/password
        """
        try:
            print("[LinkedIn Bot] Logging in...")

            # Check if we have cookies to use
            cookies = self.user.get('linkedin_cookies')
            if cookies:
                print("[LinkedIn Bot] 🍪 Using saved session cookies...")
                return self._login_with_cookies(cookies)

            # Fall back to traditional login
            print("[LinkedIn Bot] Using username/password login...")
            return self._login_with_credentials()

        except Exception as e:
            print(f"[LinkedIn Bot] Login error: {str(e)}")
            return False

    def _login_with_cookies(self, cookies):
        """
        Login using saved session cookies
        Args:
            cookies (dict): Dictionary of cookie name/value pairs
        Returns:
            bool: True if successful
        """
        try:
            # First, navigate to LinkedIn homepage
            print("[LinkedIn Bot] Loading LinkedIn homepage...")
            self.driver.get('https://www.linkedin.com')
            time.sleep(2)

            # Add each cookie to the browser
            print(f"[LinkedIn Bot] Adding {len(cookies)} cookies to browser...")
            for name, value in cookies.items():
                try:
                    self.driver.add_cookie({
                        'name': name,
                        'value': value,
                        'domain': '.linkedin.com'
                    })
                except Exception as e:
                    print(f"[LinkedIn Bot] Warning: Could not add cookie {name}: {str(e)}")

            # Navigate to feed to verify login
            print("[LinkedIn Bot] Verifying cookie-based login...")
            self.driver.get('https://www.linkedin.com/feed/')
            time.sleep(3)

            current_url = self.driver.current_url
            print(f"[LinkedIn Bot] Current URL: {current_url}")

            # Check if we're logged in
            if '/feed' in current_url or '/mynetwork' in current_url:
                print("[LinkedIn Bot] ✅ Cookie-based login successful!")
                return True
            elif '/login' in current_url or '/checkpoint' in current_url:
                print("[LinkedIn Bot] ❌ Cookies expired or invalid. Need to re-authenticate.")
                return False
            else:
                print(f"[LinkedIn Bot] ⚠️  Unexpected URL after cookie login: {current_url}")
                return False

        except Exception as e:
            print(f"[LinkedIn Bot] Cookie login error: {str(e)}")
            return False

    def _login_with_credentials(self):
        """
        Traditional login with username/password
        Returns:
            bool: True if successful
        """
        try:
            # Navigate to login page
            print("[LinkedIn Bot] Attempting to load https://www.linkedin.com/login")
            try:
                self.driver.get('https://www.linkedin.com/login')
                print(f"[LinkedIn Bot] ✅ Page loaded! Current URL: {self.driver.current_url}")
                print(f"[LinkedIn Bot] Page title: {self.driver.title}")
            except Exception as e:
                print(f"[LinkedIn Bot] ❌ Failed to load login page: {str(e)}")
                print(f"[LinkedIn Bot] This usually means LinkedIn is blocking headless browsers")
                return False

            time.sleep(3)

            # Check for CAPTCHA or security challenge
            page_source = self.driver.page_source.lower()
            if 'captcha' in page_source or 'security' in page_source or 'verify' in page_source:
                print("[LinkedIn Bot] ⚠️  Security challenge or CAPTCHA detected!")
                print(f"[LinkedIn Bot] Page title: {self.driver.title}")
                return False

            # Get credentials from user profile
            username = self.user.get('linkedin_email')
            password = self.user.get('linkedin_password')

            if not username or not password:
                print("[LinkedIn Bot] No credentials found")
                return False

            print(f"[LinkedIn Bot] Looking for username field...")
            # Enter username with shorter timeout
            try:
                username_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'username'))
                )
                username_field.clear()
                time.sleep(0.5)
                username_field.send_keys(username)
                print("[LinkedIn Bot] Username entered")
            except TimeoutException:
                print(f"[LinkedIn Bot] ❌ Username field not found. Page title: {self.driver.title}")
                print(f"[LinkedIn Bot] Current URL: {self.driver.current_url}")
                return False

            # Enter password
            try:
                password_field = self.driver.find_element(By.ID, 'password')
                password_field.clear()
                time.sleep(0.5)
                password_field.send_keys(password)
                print("[LinkedIn Bot] Password entered")
            except NoSuchElementException:
                print("[LinkedIn Bot] ❌ Password field not found")
                return False

            # Click login button
            try:
                login_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
                login_button.click()
                print("[LinkedIn Bot] Login button clicked")
            except NoSuchElementException:
                print("[LinkedIn Bot] ❌ Login button not found")
                return False

            # Wait for redirect to feed
            print("[LinkedIn Bot] Waiting for redirect after login...")
            time.sleep(8)

            # Check if login successful
            current_url = self.driver.current_url
            print(f"[LinkedIn Bot] After login, current URL: {current_url}")

            if '/feed' in current_url or '/mynetwork' in current_url or 'linkedin.com/in/' in current_url:
                print("[LinkedIn Bot] ✅ Login successful")
                return True
            elif '/checkpoint/challenge' in current_url or '/challenge' in current_url:
                print("[LinkedIn Bot] ❌ LinkedIn is showing a security challenge - manual intervention required")
                return False
            else:
                print(f"[LinkedIn Bot] ❌ Login failed - unexpected URL: {current_url}")
                return False

        except Exception as e:
            print(f"[LinkedIn Bot] Login error: {str(e)}")
            if self.driver:
                print(f"[LinkedIn Bot] Current URL at error: {self.driver.current_url}")
                print(f"[LinkedIn Bot] Page title at error: {self.driver.title}")
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

    def search_jobs(self, job_title, location=None, job_type=None, experience_level=None, remote_preference=None, keywords=None):
        """
        Search for jobs on LinkedIn

        Args:
            job_title (str): Job title to search for
            location (str): Location preference
            job_type (str): Job type (full-time, part-time, etc.)
            experience_level (str): Experience level
            remote_preference (str): Remote, hybrid, or onsite
            keywords (list): Additional keywords

        Returns:
            list: List of job dictionaries with job_url, company_name, job_title, etc.
        """
        try:
            print(f"[LinkedIn Bot] Searching for jobs: {job_title} in {location or 'Any location'}")

            # Build search URL
            search_query = job_title
            if keywords:
                search_query += ' ' + ' '.join(keywords)

            # Navigate to jobs search page
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={search_query}"
            if location:
                search_url += f"&location={location}"
            if job_type:
                # Map job types to LinkedIn filters
                job_type_mapping = {
                    'full-time': 'F',
                    'part-time': 'P',
                    'contract': 'C',
                    'temporary': 'T',
                    'internship': 'I'
                }
                jt_code = job_type_mapping.get(job_type.lower())
                if jt_code:
                    search_url += f"&f_JT={jt_code}"

            if remote_preference:
                # Map remote preferences
                if remote_preference.lower() == 'remote':
                    search_url += "&f_WT=2"  # Remote only
                elif remote_preference.lower() == 'hybrid':
                    search_url += "&f_WT=1"  # Hybrid

            # Add Easy Apply filter
            search_url += "&f_AL=true"

            print(f"[LinkedIn Bot] Navigating to: {search_url}")
            self.driver.get(search_url)
            time.sleep(5)

            # Scroll to load more jobs
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            # Find all job listings
            jobs = []
            try:
                job_cards = self.driver.find_elements(By.CSS_SELECTOR, '.jobs-search__results-list li, .scaffold-layout__list-container li')
                print(f"[LinkedIn Bot] Found {len(job_cards)} job cards")

                for card in job_cards[:20]:  # Limit to first 20 jobs
                    try:
                        # Get job link
                        link_element = card.find_element(By.CSS_SELECTOR, 'a.job-card-list__title, a.job-card-container__link')
                        job_url = link_element.get_attribute('href')

                        # Get job title
                        try:
                            job_title_elem = card.find_element(By.CSS_SELECTOR, '.job-card-list__title, .job-card-container__primary-description')
                            job_title_text = job_title_elem.text.strip()
                        except:
                            job_title_text = job_title

                        # Get company name
                        try:
                            company_elem = card.find_element(By.CSS_SELECTOR, '.job-card-container__company-name, .job-card-container__primary-description')
                            company_name = company_elem.text.strip()
                        except:
                            company_name = "Unknown Company"

                        # Get location
                        try:
                            location_elem = card.find_element(By.CSS_SELECTOR, '.job-card-container__metadata-item, .job-card-container__metadata-wrapper')
                            job_location = location_elem.text.strip()
                        except:
                            job_location = location

                        # Check for Easy Apply
                        try:
                            card.find_element(By.XPATH, ".//*[contains(text(), 'Easy Apply')]")
                            is_easy_apply = True
                        except:
                            is_easy_apply = False

                        if is_easy_apply and job_url:
                            jobs.append({
                                'job_url': job_url.split('?')[0],  # Remove query params
                                'job_title': job_title_text,
                                'company_name': company_name,
                                'location': job_location,
                                'job_type': job_type,
                                'salary_range': None
                            })
                    except Exception as e:
                        print(f"[LinkedIn Bot] Error parsing job card: {str(e)}")
                        continue

                print(f"[LinkedIn Bot] Successfully parsed {len(jobs)} jobs with Easy Apply")

            except Exception as e:
                print(f"[LinkedIn Bot] Error finding job cards: {str(e)}")

            return jobs

        except Exception as e:
            print(f"[LinkedIn Bot] Job search error: {str(e)}")
            return []

    def logout(self):
        """Logout from LinkedIn"""
        try:
            print("[LinkedIn Bot] Logging out...")
            # LinkedIn doesn't require explicit logout for bot sessions
            # Just clean up the driver
            if self.driver:
                self.driver.quit()
            print("[LinkedIn Bot] Logout complete")
        except Exception as e:
            print(f"[LinkedIn Bot] Logout error: {str(e)}")
