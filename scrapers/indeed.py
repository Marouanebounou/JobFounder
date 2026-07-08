import feedparser
from urllib.parse import quote_plus
from scrapers.base import BaseScraper


class IndeedScraper(BaseScraper):

    def __init__(self):
        super().__init__("Indeed")

    def scrape(self, keywords: list[str], location: str, max_results: int) -> list[dict]:
        jobs = []
        per_kw = max(max_results // len(keywords[:3]), 10)

        for keyword in keywords[:3]:
            url = (
                f"https://ma.indeed.com/rss?"
                f"q={quote_plus(keyword)}"
                f"&l={quote_plus(location)}"
            )
            feed = feedparser.parse(url)

            for entry in feed.entries[:per_kw]:
                if len(jobs) >= max_results:
                    break

                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                description = entry.get("summary", "").strip()
                date = entry.get("published", "").strip()
                company = entry.get("author", "N/A").strip()

                if title and link:
                    jobs.append(self.normalize_job(title, company, location, link, description, date))

        print(f"[Indeed] Found {len(jobs)} jobs")
        return jobs[:max_results]
