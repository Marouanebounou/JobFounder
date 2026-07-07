import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_APP_PASSWORD = os.getenv("SENDER_APP_PASSWORD", "")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "")

DAILY_TIME = os.getenv("DAILY_TIME", "08:00")

SEARCH_LOCATION = os.getenv("SEARCH_LOCATION", "Maroc")
SEARCH_KEYWORDS = [k.strip() for k in os.getenv("SEARCH_KEYWORDS", "").split(",") if k.strip()]
MAX_JOBS_PER_SOURCE = int(os.getenv("MAX_JOBS_PER_SOURCE", "30"))
MIN_MATCH_SCORE = int(os.getenv("MIN_MATCH_SCORE", "15"))

ENABLE_REKRUTE = os.getenv("ENABLE_REKRUTE", "true").lower() == "true"
ENABLE_EMPLOIMA = os.getenv("ENABLE_EMPLOIMA", "true").lower() == "true"
ENABLE_INDEED = os.getenv("ENABLE_INDEED", "true").lower() == "true"
ENABLE_LINKEDIN = os.getenv("ENABLE_LINKEDIN", "true").lower() == "true"
ENABLE_WELCOMEJUNGLE = os.getenv("ENABLE_WELCOMEJUNGLE", "true").lower() == "true"

AUTO_APPLY = os.getenv("AUTO_APPLY", "false").lower() == "true"
REKRUTE_EMAIL = os.getenv("REKRUTE_EMAIL", "")
REKRUTE_PASSWORD = os.getenv("REKRUTE_PASSWORD", "")
INDEED_EMAIL = os.getenv("INDEED_EMAIL", "")
INDEED_PASSWORD = os.getenv("INDEED_PASSWORD", "")

CV_PATH = ROOT_DIR / os.getenv("CV_PATH", "cv/cv.pdf")

DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
JOBS_FILE = DATA_DIR / "jobs.json"
APPLIED_FILE = DATA_DIR / "applied.json"
