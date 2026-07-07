from urllib.parse import quote_plus
from scrapers.base import BaseScraper


class LinkedInScraper(BaseScraper):

    def __init__(self):
        super().__init__("LinkedIn")
        self.base_url = "https://www.linkedin.com/jobs/search"

    def scrape(self, keywords: list[str], location: str, max_results: int) -> list[dict]:
        jobs = []
        query = " ".join(keywords) if keywords else ""
        geo_id = "102787409"
        start = 0

        while len(jobs) < max_results:
            url = (
                f"{self.base_url}?"
                f"keywords={quote_plus(query)}"
                f"&location={quote_plus(location)}"
                f"&geoId={geo_id}"
                f"&start={start}"
            )
            soup = self.fetch_page(url)
            if not soup:
                break

            cards = soup.select("div.base-card, li.result-card, div.job-search-card")
            if not cards:
                break

            for card in cards:
                if len(jobs) >= max_results:
                    break

                title_el = card.select_one("h3.base-search-card__title, span.sr-only")
                if not title_el:
                    continue

                title = title_el.get_text(strip=True)

                link_el = card.select_one("a.base-card__full-link, a.result-card__full-card-link")
                link = link_el.get("href", "") if link_el else ""

                company_el = card.select_one("h4.base-search-card__subtitle, a.hidden-nested-link")
                company = company_el.get_text(strip=True) if company_el else "N/A"

                loc_el = card.select_one("span.job-search-card__location")
                loc = loc_el.get_text(strip=True) if loc_el else location

                date_el = card.select_one("time")
                date = date_el.get("datetime", "") if date_el else ""

                jobs.append(self.normalize_job(title, company, loc, link, "", date))

            start += 25
            if start > 75:
                break

        print(f"[LinkedIn] Found {len(jobs)} jobs")
        return jobs
