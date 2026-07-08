from urllib.parse import quote_plus
from scrapers.base import BaseScraper


class RekruteScraper(BaseScraper):

    def __init__(self):
        super().__init__("Rekrute")
        self.base_url = "https://www.rekrute.com"

    def scrape(self, keywords: list[str], location: str, max_results: int) -> list[dict]:
        jobs = []
        per_kw = max(max_results // len(keywords[:3]), 5)

        for keyword in keywords[:3]:
            url = (
                f"{self.base_url}/offres.html?"
                f"s=1&p=1&o=1&searchKeyWord={quote_plus(keyword)}"
                f"&postType=0&empType=0"
            )
            for page in range(1, 4):
                if len(jobs) >= max_results:
                    break
                page_url = url + f"&page={page}"
                soup = self.fetch_page(page_url, referer=self.base_url)
                if not soup:
                    break

                items = (
                    soup.select("li[class*='post-id']") or
                    soup.select("li.highlight-target") or
                    soup.select(".section-offres li") or
                    soup.select("article.job-card") or
                    soup.select("div.job-card") or
                    soup.select(".offres li")
                )

                if not items:
                    break

                for item in items:
                    if len(jobs) >= per_kw:
                        break

                    link_el = item.select_one("h2 a, h3 a, a.titreJob, a[href*='offre']")
                    if not link_el:
                        continue

                    title = link_el.get_text(strip=True)
                    link = link_el.get("href", "")
                    if link and not link.startswith("http"):
                        link = self.base_url + link

                    company_el = item.select_one("a.company, span.company, .recruiter a, a[href*='recruteur']")
                    company = company_el.get_text(strip=True) if company_el else "N/A"

                    loc_el = item.select_one("span.location, span.city, span.ville, .loc")
                    loc = loc_el.get_text(strip=True) if loc_el else location

                    date_el = item.select_one("span.date, em.date, time")
                    date = date_el.get_text(strip=True) if date_el else ""

                    jobs.append(self.normalize_job(title, company, loc, link, "", date))

        print(f"[Rekrute] Found {len(jobs)} jobs")
        return jobs[:max_results]
