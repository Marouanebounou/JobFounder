from urllib.parse import quote_plus
from scrapers.base import BaseScraper


class EmploimaScraper(BaseScraper):

    def __init__(self):
        super().__init__("Emploi.ma")
        self.base_url = "https://www.emploi.ma"

    def scrape(self, keywords: list[str], location: str, max_results: int) -> list[dict]:
        jobs = []
        per_kw = max(max_results // len(keywords[:3]), 5)

        for keyword in keywords[:3]:
            url = f"{self.base_url}/recherche-jobs-maroc/{quote_plus(keyword)}"
            for page in range(1, 4):
                if len(jobs) >= max_results:
                    break
                page_url = f"{url}?page={page}"
                soup = self.fetch_page(page_url, referer=self.base_url)
                if not soup:
                    break

                items = (
                    soup.select("div.job-listing") or
                    soup.select("div.card-job") or
                    soup.select("article.job") or
                    soup.select("div.result-item") or
                    soup.select("div.job-item") or
                    soup.select("li.result-item")
                )

                if not items:
                    break

                for item in items:
                    if len(jobs) >= per_kw:
                        break

                    title_el = item.select_one("h2 a, h3 a, a.job-title, a.title")
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

                    jobs.append(self.normalize_job(title, company, loc, link, "", date))

        print(f"[Emploi.ma] Found {len(jobs)} jobs")
        return jobs[:max_results]
