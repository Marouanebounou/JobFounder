from urllib.parse import quote_plus
from scrapers.base import BaseScraper


class EmploimaScraper(BaseScraper):

    def __init__(self):
        super().__init__("Emploi.ma")
        self.base_url = "https://www.emploi.ma"

    def scrape(self, keywords: list[str], location: str, max_results: int) -> list[dict]:
        jobs = []
        query = " ".join(keywords) if keywords else ""
        search_url = f"{self.base_url}/recherche-jobs-maroc?q={quote_plus(query)}&l={quote_plus(location)}"

        page = 1
        while len(jobs) < max_results:
            url = f"{search_url}&page={page}"
            soup = self.fetch_page(url)
            if not soup:
                break

            listings = soup.select("div.job-listing, div.card-job, article.job")
            if not listings:
                listings = soup.select("div.result-item, div.job-item")

            if not listings:
                break

            for item in listings:
                if len(jobs) >= max_results:
                    break

                title_el = item.select_one("h2 a, h3 a, a.job-title")
                if not title_el:
                    continue

                title = title_el.get_text(strip=True)
                link = title_el.get("href", "")
                if link and not link.startswith("http"):
                    link = self.base_url + link

                company_el = item.select_one("span.company, div.company-name, a.company")
                company = company_el.get_text(strip=True) if company_el else "N/A"

                loc_el = item.select_one("span.location, span.city, div.job-location")
                loc = loc_el.get_text(strip=True) if loc_el else location

                date_el = item.select_one("span.date, time")
                date = date_el.get_text(strip=True) if date_el else ""

                desc_el = item.select_one("p.description, div.job-desc")
                desc = desc_el.get_text(strip=True) if desc_el else ""

                jobs.append(self.normalize_job(title, company, loc, link, desc, date))

            page += 1
            if page > 5:
                break

        print(f"[Emploi.ma] Found {len(jobs)} jobs")
        return jobs
