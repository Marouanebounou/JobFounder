from urllib.parse import quote_plus
from scrapers.base import BaseScraper


class IndeedScraper(BaseScraper):

    def __init__(self):
        super().__init__("Indeed")
        self.base_url = "https://ma.indeed.com"

    def scrape(self, keywords: list[str], location: str, max_results: int) -> list[dict]:
        jobs = []
        query = " ".join(keywords) if keywords else ""

        start = 0
        while len(jobs) < max_results:
            url = (
                f"{self.base_url}/jobs?"
                f"q={quote_plus(query)}"
                f"&l={quote_plus(location)}"
                f"&start={start}"
            )
            soup = self.fetch_page(url)
            if not soup:
                break

            cards = soup.select("div.job_seen_beacon, div.jobsearch-ResultsList > div")
            if not cards:
                cards = soup.select("td.resultContent, div.result")

            if not cards:
                break

            for card in cards:
                if len(jobs) >= max_results:
                    break

                title_el = card.select_one("h2.jobTitle a, a.jcs-JobTitle, h2 a")
                if not title_el:
                    continue

                title = title_el.get_text(strip=True)
                link = title_el.get("href", "")
                if link and not link.startswith("http"):
                    link = "https://ma.indeed.com" + link

                company_el = card.select_one("span.companyName, span[data-testid='company-name']")
                company = company_el.get_text(strip=True) if company_el else "N/A"

                loc_el = card.select_one("div.companyLocation, span[data-testid='text-location']")
                loc = loc_el.get_text(strip=True) if loc_el else location

                date_el = card.select_one("span.date, span.css-qvloho")
                date = date_el.get_text(strip=True) if date_el else ""

                snippet_el = card.select_one("div.job-snippet, td.snip")
                desc = snippet_el.get_text(strip=True) if snippet_el else ""

                jobs.append(self.normalize_job(title, company, loc, link, desc, date))

            start += 10
            if start > 50:
                break

        print(f"[Indeed] Found {len(jobs)} jobs")
        return jobs
