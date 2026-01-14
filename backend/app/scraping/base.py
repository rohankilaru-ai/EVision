"""
Base scraper class with common functionality
"""
import time
import random
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from ..core.config import settings


class BaseScraper(ABC):
    """Base class for all scrapers"""

    def __init__(self, use_selenium: bool = False):
        self.use_selenium = use_selenium
        self.driver: Optional[webdriver.Chrome] = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': settings.USER_AGENT
        })

    def __enter__(self):
        if self.use_selenium:
            self.init_selenium()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def init_selenium(self):
        """Initialize Selenium webdriver"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'user-agent={settings.USER_AGENT}')

        self.driver = webdriver.Chrome(options=options)

    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            self.driver.quit()
        self.session.close()

    def delay(self, min_seconds: Optional[float] = None, max_seconds: Optional[float] = None):
        """Random delay between requests"""
        min_s = min_seconds or settings.SCRAPING_DELAY
        max_s = max_seconds or (settings.SCRAPING_DELAY * 2)
        time.sleep(random.uniform(min_s, max_s))

    def get_soup(self, url: str) -> BeautifulSoup:
        """Get BeautifulSoup object from URL"""
        if self.use_selenium and self.driver:
            self.driver.get(url)
            self.delay()
            html = self.driver.page_source
        else:
            response = self.session.get(url)
            response.raise_for_status()
            html = response.text
            self.delay()

        return BeautifulSoup(html, 'lxml')

    def get_json(self, url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Get JSON response from URL"""
        response = self.session.get(url, params=params)
        response.raise_for_status()
        self.delay()
        return response.json()

    def post_json(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """POST JSON data and get JSON response"""
        response = self.session.post(url, json=data)
        response.raise_for_status()
        self.delay()
        return response.json()

    @abstractmethod
    def scrape(self) -> Any:
        """Main scraping method - to be implemented by subclasses"""
        pass
