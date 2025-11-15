"""
LinkedIn job scraper implementation
"""
import time
import re
from datetime import datetime, timedelta
from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from app.scrapers.base_scraper import BaseJobScraper


class LinkedInScraper(BaseJobScraper):
    """
    Scraper for LinkedIn Jobs
    Uses Selenium for dynamic content
    """

    def __init__(self, proxy_url=None, proxy_key=None):
        super().__init__(proxy_url, proxy_key)
        self.driver = None
        self.base_url = "https://www.linkedin.com"

    def initialize_driver(self):
        """Initialize Selenium WebDriver"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # Random user agent
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)

    def scrape(self, job_title, location, keywords=None):
        """
        Scrape LinkedIn jobs

        Args:
            job_title (str): Job title to search
            location (str): Location
            keywords (list): Additional keywords

        Returns:
            list: Job dictionaries
        """
        try:
            self.initialize_driver()

            # Build search query
            search_query = job_title
            if keywords:
                search_query += ' ' + ' '.join(keywords)

            # Build URL
            url = f"{self.base_url}/jobs/search/?" \
                  f"keywords={quote_plus(search_query)}&" \
                  f"location={quote_plus(location)}&" \
                  f"f_TPR=r604800&" \  # Jobs posted in last week
                  f"f_E=2,3"  # Entry and Mid-Senior level

            print(f"[LinkedIn] Scraping: {url}")
            self.driver.get(url)

            # Wait for job listings to load
            time.sleep(3)

            jobs = []
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, '.job-search-card')

            print(f"[LinkedIn] Found {len(job_cards)} job cards")

            for card in job_cards[:20]:  # Limit to 20 jobs per scrape
                try:
                    job_data = self._parse_job_card(card)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    print(f"[LinkedIn] Error parsing job card: {str(e)}")
                    continue

            print(f"[LinkedIn] Successfully parsed {len(jobs)} jobs")
            return jobs

        except Exception as e:
            print(f"[LinkedIn] Scraping error: {str(e)}")
            return []

        finally:
            if self.driver:
                self.driver.quit()

    def _parse_job_card(self, card):
        """Parse individual job card"""
        try:
            # Extract job title
            title_elem = card.find_element(By.CSS_SELECTOR, '.base-search-card__title')
            job_title = title_elem.text.strip()

            # Extract company name
            company_elem = card.find_element(By.CSS_SELECTOR, '.base-search-card__subtitle')
            company_name = company_elem.text.strip()

            # Extract location
            location_elem = card.find_element(By.CSS_SELECTOR, '.job-search-card__location')
            location = location_elem.text.strip()

            # Extract job URL
            link_elem = card.find_element(By.CSS_SELECTOR, 'a.base-card__full-link')
            job_url = link_elem.get_attribute('href')

            # Extract job ID from URL
            job_id_match = re.search(r'/jobs/view/(\d+)', job_url)
            external_id = job_id_match.group(1) if job_id_match else None

            if not external_id:
                return None

            # Try to extract salary (not always available)
            salary_range = None
            try:
                salary_elem = card.find_element(By.CSS_SELECTOR, '.job-search-card__salary-info')
                salary_range = salary_elem.text.strip()
            except NoSuchElementException:
                pass

            # Try to get posting date
            posted_date = None
            try:
                date_elem = card.find_element(By.CSS_SELECTOR, '.job-search-card__listdate')
                date_text = date_elem.get_attribute('datetime')
                if date_text:
                    posted_date = datetime.fromisoformat(date_text.replace('Z', '+00:00'))
            except NoSuchElementException:
                posted_date = datetime.utcnow()

            # Get job details by visiting the job page (optional, can be slow)
            description = ""
            requirements = ""
            job_type = "Full-time"  # Default

            return {
                'platform': 'LinkedIn',
                'external_id': external_id,
                'company_name': company_name,
                'job_title': job_title,
                'location': location,
                'salary_range': salary_range,
                'job_type': job_type,
                'description': description,
                'requirements': requirements,
                'job_url': job_url,
                'posted_date': posted_date
            }

        except Exception as e:
            print(f"[LinkedIn] Error parsing job card: {str(e)}")
            return None

    def get_job_details(self, job_url):
        """
        Get detailed job information
        (Called separately to avoid slowing down initial scrape)
        """
        try:
            self.driver.get(job_url)
            time.sleep(2)

            # Wait for description to load
            description_elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.show-more-less-html__markup'))
            )

            description = description_elem.text.strip()

            # Try to extract job type
            job_type = "Full-time"
            try:
                criteria_list = self.driver.find_elements(By.CSS_SELECTOR, '.description__job-criteria-item')
                for criteria in criteria_list:
                    label = criteria.find_element(By.CSS_SELECTOR, '.description__job-criteria-subheader').text
                    if 'Employment type' in label:
                        job_type = criteria.find_element(By.CSS_SELECTOR, '.description__job-criteria-text').text.strip()
                        break
            except:
                pass

            return {
                'description': description,
                'job_type': job_type
            }

        except Exception as e:
            print(f"[LinkedIn] Error getting job details: {str(e)}")
            return {
                'description': '',
                'job_type': 'Full-time'
            }
