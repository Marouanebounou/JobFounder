from urllib.parse import quote_plus
from scrapers.base import BaseScraper


class RekruteScraper(BaseScraper):

    def __init__(self):
        super().__init__("Rekrute")
        self.base_url = "https://www.rekrute.com"

    def scrape(self, keywords: list[str], location: str, max_results: int) -> list[dict]:
        jobs = []
        query = " ".join(keywords) if keywords else ""
        search_url = (
            f"{self.base_url}/fr/offres.html?"
            f"s=1&p=1&o=1"
            f"&keyword={quote_plus(query)}"
            f"&location={quote_plus(location)}"
        )

        page = 1
        while len(jobs) < max_results:
            url = search_url + f"&page={page}"
            soup = self.fetch_page(url)
            if not soup:
                break

            listings = soup.select("li.post-id")
            if not listings:
                listings = soup.select("div.section-content ul li")

            if not listings:
                break

            for item in listings:
                if len(jobs) >= max_results:
                    break

                title_el = item.select_one("a.titreJob, h2 a")
                if not title_el:
                    continue

                title = title_el.get_text(strip=True)
                link = title_el.get("href", "")
                if link and not link.startswith("http"):
                    link = self.base_url + link

                company_el = item.select_one("span.company, a.entreprise")
                company = company_el.get_text(strip=True) if company_el else "N/A"

                loc_el = item.select_one("span.location, span.city")
                loc = loc_el.get_text(strip=True) if loc_el else location

                date_el = item.select_one("span.date, em.date")
                date = date_el.get_text(strip=True) if date_el else ""

                desc_el = item.select_one("p, div.info")
                desc = desc_el.get_text(strip=True) if desc_el else ""

                jobs.append(self.normalize_job(title, company, loc, link, desc, date))

            page += 1
            if page > 5:
                break

        print(f"[Rekrute] Found {len(jobs)} jobs")
        return jobs
