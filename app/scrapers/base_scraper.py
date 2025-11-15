"""
Base class for job scrapers
"""
from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup


class BaseJobScraper(ABC):
    """
    Base class for platform-specific job scrapers

    Each platform should extend this and implement scraping logic
    """

    def __init__(self, proxy_url=None, proxy_key=None):
        """
        Initialize scraper

        Args:
            proxy_url (str): Proxy service URL (optional)
            proxy_key (str): Proxy API key (optional)
        """
        self.proxy_url = proxy_url
        self.proxy_key = proxy_key
        self.session = requests.Session()

    @abstractmethod
    def scrape(self, job_title, location, keywords=None):
        """
        Scrape jobs from platform

        Args:
            job_title (str): Job title to search for
            location (str): Location to search in
            keywords (list): Additional keywords

        Returns:
            list: List of job dictionaries with structure:
                {
                    'platform': str,
                    'external_id': str,
                    'company_name': str,
                    'job_title': str,
                    'location': str,
                    'salary_range': str (optional),
                    'job_type': str (optional),
                    'description': str,
                    'requirements': str (optional),
                    'job_url': str,
                    'posted_date': datetime (optional)
                }
        """
        pass

    def make_request(self, url, method='GET', **kwargs):
        """
        Make HTTP request with proxy support

        Args:
            url (str): URL to request
            method (str): HTTP method
            **kwargs: Additional arguments for requests

        Returns:
            requests.Response
        """
        if self.proxy_url and self.proxy_key:
            # Use proxy service
            kwargs['proxies'] = {
                'http': f'{self.proxy_url}?api_key={self.proxy_key}',
                'https': f'{self.proxy_url}?api_key={self.proxy_key}'
            }

        if method == 'GET':
            return self.session.get(url, **kwargs)
        elif method == 'POST':
            return self.session.post(url, **kwargs)

    def parse_html(self, html_content):
        """
        Parse HTML content with BeautifulSoup

        Args:
            html_content (str): HTML content

        Returns:
            BeautifulSoup: Parsed HTML
        """
        return BeautifulSoup(html_content, 'lxml')
