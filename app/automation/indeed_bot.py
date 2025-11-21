"""
Indeed application automation bot
"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from app.automation.bot_base import JobApplicationBot


class IndeedBot(JobApplicationBot):
    """
    Automated job application bot for Indeed
    """

    def initialize_browser(self):
        """Initialize Selenium WebDriver"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # Set Chrome binary location (required on some systems)
        options.binary_location = '/usr/bin/google-chrome-stable'

        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 15)

        return self.driver

    def login(self):
        """Login to Indeed"""
        try:
            print("[Indeed Bot] Logging in...")

            self.driver.get('https://secure.indeed.com/account/login')
            time.sleep(2)

            # Get credentials
            email = self.user.get('indeed_email')
            password = self.user.get('indeed_password')

            if not email or not password:
                print("[Indeed Bot] No credentials found")
                return False

            # Enter email
            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, 'login-email-input'))
            )
            email_field.clear()
            email_field.send_keys(email)

            # Enter password
            password_field = self.driver.find_element(By.ID, 'login-password-input')
            password_field.clear()
            password_field.send_keys(password)

            # Click login
            login_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
            login_button.click()

            time.sleep(5)

            # Check if login successful
            if 'indeed.com/account' in self.driver.current_url or '/jobs' in self.driver.current_url:
                print("[Indeed Bot] Login successful")
                return True
            else:
                print("[Indeed Bot] Login failed")
                return False

        except Exception as e:
            print(f"[Indeed Bot] Login error: {str(e)}")
            return False

    def navigate_to_job(self, job_url):
        """Navigate to job posting"""
        try:
            print(f"[Indeed Bot] Navigating to: {job_url}")
            self.driver.get(job_url)
            time.sleep(3)

            # Check if apply button exists
            try:
                apply_button = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#indeedApplyButton, .indeed-apply-button'))
                )
                return True
            except TimeoutException:
                print("[Indeed Bot] Apply button not found")
                return False

        except Exception as e:
            print(f"[Indeed Bot] Navigation error: {str(e)}")
            return False

    def fill_application_form(self):
        """Fill Indeed application form"""
        try:
            print("[Indeed Bot] Filling application form...")

            # Click apply button
            apply_button = self.driver.find_element(By.CSS_SELECTOR, '#indeedApplyButton, .indeed-apply-button')
            apply_button.click()
            time.sleep(3)

            # Indeed forms can be in iframe
            try:
                iframe = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[name="indeed-ia-container"]'))
                )
                self.driver.switch_to.frame(iframe)
                print("[Indeed Bot] Switched to application iframe")
            except TimeoutException:
                print("[Indeed Bot] No iframe found, continuing...")

            # Fill all text inputs
            self._fill_text_fields()

            # Fill dropdowns
            self._fill_dropdowns()

            # Handle checkboxes and radio buttons
            self._handle_choices()

            return True

        except Exception as e:
            print(f"[Indeed Bot] Form filling error: {str(e)}")
            return False

    def _fill_text_fields(self):
        """Fill text input fields"""
        try:
            inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"], input[type="tel"], input[type="email"]')

            for input_field in inputs:
                try:
                    field_name = input_field.get_attribute('name') or ''
                    field_id = input_field.get_attribute('id') or ''
                    field_label = field_name.lower() + field_id.lower()

                    # Skip if already filled
                    if input_field.get_attribute('value'):
                        continue

                    # Map fields
                    if 'phone' in field_label or 'mobile' in field_label:
                        if self.user.get('phone'):
                            input_field.send_keys(self.user['phone'])

                    elif 'email' in field_label:
                        if self.user.get('email'):
                            input_field.send_keys(self.user['email'])

                    elif 'name' in field_label and 'first' in field_label:
                        if self.user.get('full_name'):
                            first_name = self.user['full_name'].split()[0]
                            input_field.send_keys(first_name)

                    elif 'name' in field_label and 'last' in field_label:
                        if self.user.get('full_name'):
                            parts = self.user['full_name'].split()
                            last_name = parts[-1] if len(parts) > 1 else ''
                            input_field.send_keys(last_name)

                    elif 'city' in field_label or 'location' in field_label:
                        if self.user.get('location'):
                            input_field.send_keys(self.user['location'])

                except Exception as e:
                    continue

        except Exception as e:
            print(f"[Indeed Bot] Error filling text fields: {str(e)}")

    def _fill_dropdowns(self):
        """Fill dropdown/select fields"""
        try:
            selects = self.driver.find_elements(By.TAG_NAME, 'select')

            for select_elem in selects:
                try:
                    select = Select(select_elem)

                    # Get field name/label
                    field_name = select_elem.get_attribute('name') or ''

                    # For education/experience dropdowns, select middle option
                    if 'education' in field_name.lower():
                        options = select.options
                        if len(options) > 2:
                            select.select_by_index(len(options) // 2)

                    elif 'experience' in field_name.lower() or 'years' in field_name.lower():
                        # Select based on user's experience
                        years = self.user.get('years_experience', 3)
                        options = select.options

                        for idx, option in enumerate(options):
                            if str(years) in option.text:
                                select.select_by_index(idx)
                                break

                    else:
                        # Default to first non-empty option
                        if len(select.options) > 1:
                            select.select_by_index(1)

                except Exception as e:
                    continue

        except Exception as e:
            print(f"[Indeed Bot] Error filling dropdowns: {str(e)}")

    def _handle_choices(self):
        """Handle radio buttons and checkboxes"""
        try:
            # Radio buttons (usually screening questions)
            radio_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')

            # Group by name
            radio_groups = {}
            for radio in radio_buttons:
                name = radio.get_attribute('name')
                if name not in radio_groups:
                    radio_groups[name] = []
                radio_groups[name].append(radio)

            # Select first option in each group (usually "Yes" or safest answer)
            for name, radios in radio_groups.items():
                try:
                    if radios and not any(r.is_selected() for r in radios):
                        # Check if any option contains "yes"
                        yes_option = None
                        for radio in radios:
                            label = self._get_label_for_input(radio)
                            if label and 'yes' in label.lower():
                                yes_option = radio
                                break

                        if yes_option:
                            yes_option.click()
                        else:
                            radios[0].click()
                except:
                    pass

        except Exception as e:
            print(f"[Indeed Bot] Error handling choices: {str(e)}")

    def _get_label_for_input(self, input_elem):
        """Get label text for input element"""
        try:
            input_id = input_elem.get_attribute('id')
            if input_id:
                label = self.driver.find_element(By.CSS_SELECTOR, f'label[for="{input_id}"]')
                return label.text
        except:
            pass
        return ''

    def upload_resume(self):
        """Upload resume"""
        try:
            print("[Indeed Bot] Looking for resume upload...")

            # Look for file upload input
            try:
                file_input = self.driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')

                # Save resume to temp file
                resume_path = self.save_resume_to_file()

                # Upload file
                file_input.send_keys(resume_path)
                time.sleep(2)

                print("[Indeed Bot] Resume uploaded")
                return True

            except NoSuchElementException:
                print("[Indeed Bot] No resume upload field (might not be required)")
                return True

        except Exception as e:
            print(f"[Indeed Bot] Resume upload error: {str(e)}")
            return True  # Don't fail application if resume upload fails

    def submit_application(self):
        """Submit the application"""
        try:
            print("[Indeed Bot] Submitting application...")

            # Look for submit/apply button
            submit_selectors = [
                'button[type="submit"]',
                'button.ia-continueButton',
                'button[id*="apply"]',
                'button[class*="submit"]'
            ]

            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if submit_button and submit_button.is_enabled():
                        break
                except NoSuchElementException:
                    continue

            if not submit_button:
                print("[Indeed Bot] Submit button not found")
                return False

            submit_button.click()
            time.sleep(5)

            # Check for confirmation
            try:
                # Switch back to main frame if in iframe
                self.driver.switch_to.default_content()

                # Look for success message
                success_indicators = [
                    'application sent',
                    'application submitted',
                    'successfully applied',
                    'thanks for applying'
                ]

                page_text = self.driver.find_element(By.TAG_NAME, 'body').text.lower()

                for indicator in success_indicators:
                    if indicator in page_text:
                        print("[Indeed Bot] Application submitted successfully")
                        return True

            except:
                pass

            print("[Indeed Bot] Application submitted (confirmation not clear but no error)")
            return True

        except Exception as e:
            print(f"[Indeed Bot] Submission error: {str(e)}")
            return False
