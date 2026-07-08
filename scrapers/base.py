import time
import random
import cloudscraper
from bs4 import BeautifulSoup


class BaseScraper:

    def __init__(self, name: str):
        self.name = name
        self.session = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )

    def fetch_page(self, url: str, referer: str = "") -> BeautifulSoup | None:
        try:
            time.sleep(random.uniform(2.0, 4.0))
            headers = {"Referer": referer} if referer else {}
            response = self.session.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            return BeautifulSoup(response.text, "lxml")
        except Exception as e:
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
