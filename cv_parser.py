import re
from pathlib import Path
from pdfminer.high_level import extract_text


SKILL_PATTERNS = [
    "python", "javascript", "typescript", "java", "c\\+\\+", "c#", "php", "ruby",
    "go", "rust", "swift", "kotlin", "dart", "sql", "html", "css", "sass",
    "django", "flask", "fastapi", "express", "react", "angular", "vue",
    "next\\.?js", "node\\.?js", "spring", "laravel", "flutter", "docker",
    "kubernetes", "terraform", "aws", "azure", "gcp",
    "machine learning", "deep learning", "data science", "data analysis",
    "pandas", "numpy", "tensorflow", "pytorch", "scikit-learn", "power ?bi",
    "tableau", "excel", "mongodb", "postgresql", "mysql", "redis",
    "git", "linux", "agile", "scrum", "jira", "figma", "photoshop",
    "autocad", "solidworks", "matlab", "simulink",
]

LANGUAGE_PATTERNS = [
    "fran[cc]ais", "anglais", "english", "french", "arabic", "arabe",
    "espagnol", "spanish", "allemand", "german", "italian", "italien",
]


def extract_cv_text(cv_path: Path) -> str:
    if not cv_path.exists():
        raise FileNotFoundError(f"CV not found at: {cv_path}")
    return extract_text(str(cv_path))


def extract_skills(text: str) -> list[str]:
    text_lower = text.lower()
    found = []
    for pattern in SKILL_PATTERNS:
        if re.search(r'\b' + pattern + r'\b', text_lower):
            clean = pattern.replace("\\+\\+", "++").replace("\\.", ".").replace("?", "")
            found.append(clean)
    return found


def extract_languages(text: str) -> list[str]:
    text_lower = text.lower()
    found = []
    for pattern in LANGUAGE_PATTERNS:
        if re.search(pattern, text_lower):
            clean = pattern.replace("[cc]", "c").replace("?", "")
            found.append(clean)
    return found


def extract_keywords(text: str) -> list[str]:
    stop_words = {
        "le", "la", "les", "de", "du", "des", "un", "une", "et", "en", "au",
        "aux", "pour", "par", "sur", "dans", "avec", "est", "sont", "the",
        "and", "for", "with", "from", "that", "this", "was", "are", "has",
        "been", "qui", "que", "ces", "ses", "mais", "ou", "donc",
    }
    words = re.findall(r'\b[a-zA-Z\u00C0-\u00FF]{3,}\b', text.lower())
    word_freq = {}
    for w in words:
        if w not in stop_words:
            word_freq[w] = word_freq.get(w, 0) + 1

    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [w for w, _ in sorted_words[:50]]


def parse_cv(cv_path: Path) -> dict:
    text = extract_cv_text(cv_path)
    return {
        "raw_text": text,
        "skills": extract_skills(text),
        "languages": extract_languages(text),
        "keywords": extract_keywords(text),
    }


if __name__ == "__main__":
    from config import CV_PATH
    profile = parse_cv(CV_PATH)
    print(f"Skills found: {profile['skills']}")
    print(f"Languages: {profile['languages']}")
    print(f"Top keywords: {profile['keywords'][:20]}")
