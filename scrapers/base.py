import time
import random
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class BaseScraper:

    def __init__(self, name: str):
        self.name = name
        self.ua = UserAgent()
        self.session = requests.Session()
        self.jobs = []

    def get_headers(self) -> dict:
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    def fetch_page(self, url: str) -> BeautifulSoup | None:
        try:
            time.sleep(random.uniform(1.5, 3.5))
            response = self.session.get(url, headers=self.get_headers(), timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.text, "lxml")
        except requests.RequestException as e:
            print(f"[{self.name}] Error fetching {url}: {e}")
            return None

    def scrape(self, keywords: list[str], location: str, max_results: int) -> list[dict]:
        raise NotImplementedError

    def normalize_job(self, title: str, company: str, location: str, url: str,
                      description: str = "", date: str = "") -> dict:
        return {
            "title": title.strip(),
            "company": company.strip(),
            "location": location.strip(),
            "url": url.strip(),
            "description": description.strip(),
            "date": date.strip(),
            "source": self.name,
        }
