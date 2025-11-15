"""
Indeed job scraper implementation
"""
import time
import re
from datetime import datetime, timedelta
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from app.scrapers.base_scraper import BaseJobScraper


class IndeedScraper(BaseJobScraper):
    """
    Scraper for Indeed jobs
    Uses requests + BeautifulSoup (faster than Selenium)
    """

    def __init__(self, proxy_url=None, proxy_key=None):
        super().__init__(proxy_url, proxy_key)
        self.base_url = "https://www.indeed.com"

    def scrape(self, job_title, location, keywords=None):
        """
        Scrape Indeed jobs

        Args:
            job_title (str): Job title
            location (str): Location
            keywords (list): Additional keywords

        Returns:
            list: Job dictionaries
        """
        try:
            # Build search query
            search_query = job_title
            if keywords:
                search_query += ' ' + ' '.join(keywords)

            # Build URL
            url = f"{self.base_url}/jobs?" \
                  f"q={quote_plus(search_query)}&" \
                  f"l={quote_plus(location)}&" \
                  f"fromage=7&" \  # Last 7 days
                  f"sort=date"  # Sort by date

            print(f"[Indeed] Scraping: {url}")

            # Make request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }

            response = self.make_request(url, headers=headers)

            if response.status_code != 200:
                print(f"[Indeed] Failed to fetch jobs: {response.status_code}")
                return []

            soup = self.parse_html(response.text)

            # Find job cards
            job_cards = soup.find_all('div', class_='job_seen_beacon')

            print(f"[Indeed] Found {len(job_cards)} job cards")

            jobs = []
            for card in job_cards[:20]:  # Limit to 20 jobs
                try:
                    job_data = self._parse_job_card(card)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    print(f"[Indeed] Error parsing job card: {str(e)}")
                    continue

            print(f"[Indeed] Successfully parsed {len(jobs)} jobs")
            return jobs

        except Exception as e:
            print(f"[Indeed] Scraping error: {str(e)}")
            return []

    def _parse_job_card(self, card):
        """Parse individual job card"""
        try:
            # Extract job title
            title_elem = card.find('h2', class_='jobTitle')
            if not title_elem:
                return None

            job_title_link = title_elem.find('a')
            if not job_title_link:
                job_title = title_elem.get_text(strip=True)
                job_key = None
            else:
                job_title = job_title_link.get_text(strip=True)
                # Extract job key from data attribute or href
                job_key = job_title_link.get('data-jk') or job_title_link.get('id', '').replace('job_', '')

            if not job_key:
                return None

            # Extract company name
            company_elem = card.find('span', class_='companyName')
            company_name = company_elem.get_text(strip=True) if company_elem else 'Unknown'

            # Extract location
            location_elem = card.find('div', class_='companyLocation')
            location = location_elem.get_text(strip=True) if location_elem else 'Remote'

            # Extract salary (if available)
            salary_range = None
            salary_elem = card.find('div', class_='salary-snippet')
            if salary_elem:
                salary_range = salary_elem.get_text(strip=True)

            # Extract job snippet/description
            snippet_elem = card.find('div', class_='job-snippet')
            description = snippet_elem.get_text(strip=True) if snippet_elem else ''

            # Build job URL
            job_url = f"{self.base_url}/viewjob?jk={job_key}"

            # Extract posting date
            date_elem = card.find('span', class_='date')
            posted_date = self._parse_date(date_elem.get_text(strip=True) if date_elem else '')

            # Job type (usually need to visit job page for this)
            job_type = "Full-time"  # Default

            return {
                'platform': 'Indeed',
                'external_id': job_key,
                'company_name': company_name,
                'job_title': job_title,
                'location': location,
                'salary_range': salary_range,
                'job_type': job_type,
                'description': description,
                'requirements': '',
                'job_url': job_url,
                'posted_date': posted_date
            }

        except Exception as e:
            print(f"[Indeed] Error parsing job card: {str(e)}")
            return None

    def _parse_date(self, date_text):
        """Parse relative date text to datetime"""
        try:
            date_text = date_text.lower()

            if 'just posted' in date_text or 'today' in date_text:
                return datetime.utcnow()

            elif 'yesterday' in date_text:
                return datetime.utcnow() - timedelta(days=1)

            elif 'day' in date_text:
                # "2 days ago"
                days = int(re.search(r'(\d+)', date_text).group(1))
                return datetime.utcnow() - timedelta(days=days)

            elif 'hour' in date_text:
                # "5 hours ago"
                hours = int(re.search(r'(\d+)', date_text).group(1))
                return datetime.utcnow() - timedelta(hours=hours)

            else:
                return datetime.utcnow()

        except:
            return datetime.utcnow()

    def get_job_details(self, job_url):
        """Get full job details"""
        try:
            response = self.make_request(job_url)

            if response.status_code != 200:
                return {}

            soup = self.parse_html(response.text)

            # Get full description
            desc_elem = soup.find('div', id='jobDescriptionText')
            description = desc_elem.get_text(strip=True) if desc_elem else ''

            # Get job type
            job_type = "Full-time"
            job_meta = soup.find_all('div', class_='jobsearch-JobMetadataHeader-item')
            for meta in job_meta:
                text = meta.get_text(strip=True).lower()
                if 'part-time' in text:
                    job_type = 'Part-time'
                elif 'contract' in text:
                    job_type = 'Contract'
                elif 'temporary' in text:
                    job_type = 'Temporary'

            return {
                'description': description,
                'job_type': job_type
            }

        except Exception as e:
            print(f"[Indeed] Error getting job details: {str(e)}")
            return {}
