import json
import time
import schedule
from datetime import date, datetime

from config import (
    CV_PATH, SEARCH_KEYWORDS, SEARCH_LOCATION, MAX_JOBS_PER_SOURCE,
    MIN_MATCH_SCORE, DAILY_TIME, JOBS_FILE,
    ENABLE_REKRUTE, ENABLE_EMPLOIMA, ENABLE_INDEED,
    ENABLE_LINKEDIN, ENABLE_WELCOMEJUNGLE,
)
from cv_parser import parse_cv
from matcher import get_top_jobs
from notifier import send_digest


def load_seen_urls() -> set:
    if JOBS_FILE.exists():
        try:
            data = json.loads(JOBS_FILE.read_text(encoding="utf-8"))
            return set(job.get("url", "") for job in data)
        except json.JSONDecodeError:
            return set()
    return set()


def save_jobs(jobs: list[dict]):
    existing = []
    if JOBS_FILE.exists():
        try:
            existing = json.loads(JOBS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = []

    existing.extend(jobs)
    JOBS_FILE.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")


def run_pipeline():
    print(f"\n{'='*60}")
    print(f"  JobFounder - Running pipeline at {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}\n")

    print("[1/4] Parsing your CV...")
    try:
        profile = parse_cv(CV_PATH)
        print(f"  -> Skills: {', '.join(profile['skills'][:10])}")
        print(f"  -> Keywords: {len(profile['keywords'])} extracted")
    except FileNotFoundError:
        print(f"  X CV not found at {CV_PATH}")
        print(f"  -> Place your CV at: {CV_PATH}")
        return

    keywords = SEARCH_KEYWORDS if SEARCH_KEYWORDS else profile["skills"][:3]
    if not keywords:
        keywords = ["développeur", "stage", "ingénieur"]
    print(f"  -> Searching for: {', '.join(keywords)}...")

    print("\n[2/4] Scraping job boards...")
    all_jobs = []

    if ENABLE_REKRUTE:
        from scrapers.rekrute import RekruteScraper
        all_jobs.extend(RekruteScraper().scrape(keywords, SEARCH_LOCATION, MAX_JOBS_PER_SOURCE))

    if ENABLE_EMPLOIMA:
        from scrapers.emploima import EmploimaScraper
        all_jobs.extend(EmploimaScraper().scrape(keywords, SEARCH_LOCATION, MAX_JOBS_PER_SOURCE))

    if ENABLE_INDEED:
        from scrapers.indeed import IndeedScraper
        all_jobs.extend(IndeedScraper().scrape(keywords, SEARCH_LOCATION, MAX_JOBS_PER_SOURCE))

    if ENABLE_LINKEDIN:
        from scrapers.linkedin import LinkedInScraper
        all_jobs.extend(LinkedInScraper().scrape(keywords, SEARCH_LOCATION, MAX_JOBS_PER_SOURCE))

    if ENABLE_WELCOMEJUNGLE:
        from scrapers.welcomejungle import WelcomeJungleScraper
        all_jobs.extend(WelcomeJungleScraper().scrape(keywords, SEARCH_LOCATION, MAX_JOBS_PER_SOURCE))

    print(f"\n  -> Total raw jobs: {len(all_jobs)}")

    seen_urls = load_seen_urls()
    new_jobs = [j for j in all_jobs if j.get("url") and j["url"] not in seen_urls]
    print(f"  -> New jobs (not seen before): {len(new_jobs)}")

    if not new_jobs:
        print("\n  No new jobs today. Will check again tomorrow.")
        return

    print("\n[3/4] Matching jobs to your profile...")
    top_jobs = get_top_jobs(new_jobs, profile, min_score=MIN_MATCH_SCORE, top_n=25)
    print(f"  -> {len(top_jobs)} jobs matched (>= {MIN_MATCH_SCORE}% relevance)")

    if top_jobs:
        print(f"  -> Best match: {top_jobs[0]['title']} @ {top_jobs[0]['company']} ({top_jobs[0]['match_score']}%)")

    print("\n[4/4] Sending email digest...")
    success = send_digest(top_jobs)

    for job in top_jobs:
        job["found_date"] = date.today().isoformat()
    save_jobs(top_jobs)

    if success:
        print(f"\nDone! {len(top_jobs)} jobs sent to your inbox.")
    else:
        print(f"\nPipeline finished but email failed. Check your .env settings.")

    print(f"{'='*60}\n")


def run_scheduler():
    print(f"JobFounder - Scheduler started")
    print(f"Will run every day at {DAILY_TIME}")
    print(f"Press Ctrl+C to stop\n")

    run_pipeline()

    schedule.every().day.at(DAILY_TIME).do(run_pipeline)

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nScheduler stopped.")


if __name__ == "__main__":
    import sys

    if "--once" in sys.argv:
        run_pipeline()
    else:
        run_scheduler()
