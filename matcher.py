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
        job.get("company", ""),
        job.get("description", ""),
        job.get("location", ""),
    ]
    return " ".join(parts)


def rank_jobs(jobs: list[dict], profile: dict, min_score: int = 15) -> list[dict]:
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
        score = int(similarities[i] * 100)
        if score >= min_score:
            job["match_score"] = score
            scored_jobs.append(job)

    scored_jobs.sort(key=lambda x: x["match_score"], reverse=True)
    return scored_jobs


def get_top_jobs(jobs: list[dict], profile: dict, min_score: int = 15, top_n: int = 20) -> list[dict]:
    ranked = rank_jobs(jobs, profile, min_score)
    return ranked[:top_n]
