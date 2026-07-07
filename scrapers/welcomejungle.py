from urllib.parse import quote_plus
from scrapers.base import BaseScraper


class WelcomeJungleScraper(BaseScraper):

    def __init__(self):
        super().__init__("WelcomeToTheJungle")
        self.base_url = "https://www.welcometothejungle.com"

    def scrape(self, keywords: list[str], location: str, max_results: int) -> list[dict]:
        jobs = []
        query = " ".join(keywords) if keywords else ""

        url = (
            f"{self.base_url}/fr/jobs?"
            f"query={quote_plus(query)}"
            f"&page=1"
            f"&aroundQuery={quote_plus(location)}"
        )

        page = 1
        while len(jobs) < max_results:
            page_url = f"{url}&page={page}"
            soup = self.fetch_page(page_url)
            if not soup:
                break

            cards = soup.select("div[data-testid='search-results-list-item-wrapper']")
            if not cards:
                cards = soup.select("article, div.ais-Hits-item, li.ais-Hits-item")

            if not cards:
                break

            for card in cards:
                if len(jobs) >= max_results:
                    break

                title_el = card.select_one("h4, h3, span[data-testid='job-title']")
                if not title_el:
                    continue

                title = title_el.get_text(strip=True)

                link_el = card.select_one("a")
                link = link_el.get("href", "") if link_el else ""
                if link and not link.startswith("http"):
                    link = self.base_url + link

                company_el = card.select_one("span[data-testid='company-name'], p, h3 + span")
                company = company_el.get_text(strip=True) if company_el else "N/A"

                loc_el = card.select_one("span[data-testid='job-location'], span.sc-")
                loc = loc_el.get_text(strip=True) if loc_el else location

                jobs.append(self.normalize_job(title, company, loc, link, "", ""))

            page += 1
            if page > 3:
                break

        print(f"[WelcomeToTheJungle] Found {len(jobs)} jobs")
        return jobs
