from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def build_profile_text(profile: dict) -> str:
    parts = []
    parts.append(" ".join(profile.get("skills", [])))
    parts.append(" ".join(profile.get("languages", [])))
    parts.append(" ".join(profile.get("keywords", [])))
    return " ".join(parts)


def build_job_text(job: dict) -> str:
    parts = [
        job.get("title", ""),
        job.get("title", ""),
        job.get("company", ""),
        job.get("description", ""),
        job.get("location", ""),
    ]
    return " ".join(parts)


def keyword_score(job: dict, profile: dict) -> int:
    job_text = build_job_text(job).lower()
    skills = profile.get("skills", [])
    if not skills:
        return 0
    matches = sum(1 for skill in skills if skill.lower() in job_text)
    return int((matches / max(len(skills), 1)) * 100)


def rank_jobs(jobs: list[dict], profile: dict, min_score: int = 5) -> list[dict]:
    if not jobs:
        return []

    profile_text = build_profile_text(profile)
    job_texts = [build_job_text(job) for job in jobs]
    all_texts = [profile_text] + job_texts

    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words=None,
        ngram_range=(1, 2),
    )
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    profile_vector = tfidf_matrix[0:1]
    job_vectors = tfidf_matrix[1:]
    similarities = cosine_similarity(profile_vector, job_vectors)[0]

    scored_jobs = []
    for i, job in enumerate(jobs):
        tfidf_score = similarities[i] * 100
        kw_score = keyword_score(job, profile)
        final_score = int(max(tfidf_score, kw_score, (tfidf_score + kw_score) / 2))
        if final_score >= min_score:
            job["match_score"] = final_score
            scored_jobs.append(job)

    scored_jobs.sort(key=lambda x: x["match_score"], reverse=True)
    return scored_jobs


def get_top_jobs(jobs: list[dict], profile: dict, min_score: int = 5, top_n: int = 25) -> list[dict]:
    ranked = rank_jobs(jobs, profile, min_score)
    return ranked[:top_n]
