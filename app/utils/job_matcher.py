import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def extract_keywords(text):
    """Extract keywords from text"""
    if not text:
        return []

    # Remove special characters and convert to lowercase
    text = re.sub(r'[^a-zA-Z\s]', '', text.lower())

    # Split into words and filter common words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'with', 'to', 'for', 'of', 'on', 'at', 'from', 'by'}
    words = [word for word in text.split() if word not in stop_words and len(word) > 2]

    return list(set(words))


def calculate_keyword_match(user_keywords, job_text):
    """Calculate keyword match score using TF-IDF similarity"""
    if not user_keywords or not job_text:
        return 0.0

    try:
        # Combine user keywords into a single string
        user_text = ' '.join(user_keywords)

        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([user_text, job_text])

        # Calculate cosine similarity
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

        return float(similarity * 100)  # Return as percentage
    except Exception:
        return 0.0


def is_remote(job_listing):
    """Check if job is remote"""
    if not job_listing.location:
        return False

    remote_keywords = ['remote', 'work from home', 'wfh', 'anywhere', 'distributed']
    location_lower = job_listing.location.lower()

    return any(keyword in location_lower for keyword in remote_keywords)


def extract_salary_from_range(salary_range):
    """Extract minimum salary from range string"""
    if not salary_range:
        return 0

    try:
        # Remove currency symbols and commas
        cleaned = re.sub(r'[$,k]', '', salary_range.lower())

        # Find numbers
        numbers = re.findall(r'\d+', cleaned)

        if not numbers:
            return 0

        # Return the minimum number (first one usually)
        min_salary = int(numbers[0])

        # If it looks like it's in thousands (e.g., "80k"), multiply by 1000
        if 'k' in salary_range.lower() and min_salary < 1000:
            min_salary *= 1000

        return min_salary
    except Exception:
        return 0


def job_salary_meets_minimum(job_listing, min_salary):
    """Check if job salary meets minimum requirement"""
    if not min_salary:
        return True

    job_min_salary = extract_salary_from_range(job_listing.salary_range)

    return job_min_salary >= min_salary


def calculate_match_score(job_listing, user_config, user_skills):
    """
    Calculate how well a job matches user preferences
    Returns a score from 0-100
    """
    score = 0
    weights = {
        'keywords': 40,
        'location': 20,
        'salary': 20,
        'experience': 10,
        'job_type': 10
    }

    # 1. Keyword matching (40%)
    if user_config.primary_keywords or user_skills:
        all_keywords = (user_config.primary_keywords or []) + (user_skills or [])
        job_text = f"{job_listing.description or ''} {job_listing.requirements or ''}"
        keyword_score = calculate_keyword_match(all_keywords, job_text)
        score += (keyword_score / 100) * weights['keywords']

    # 2. Location matching (20%)
    if user_config.primary_location:
        if job_listing.location:
            if user_config.primary_location.lower() in job_listing.location.lower():
                score += weights['location']
            elif is_remote(job_listing):
                score += weights['location'] * 0.8  # Remote jobs get 80% of location score

    # 3. Salary matching (20%)
    if user_config.primary_min_salary:
        if job_salary_meets_minimum(job_listing, user_config.primary_min_salary):
            score += weights['salary']
    else:
        # If no salary requirement, give full points
        score += weights['salary']

    # 4. Experience level matching (10%)
    if user_config.primary_experience_level and job_listing.description:
        if user_config.primary_experience_level.lower() in job_listing.description.lower():
            score += weights['experience']

    # 5. Job type matching (10%)
    if user_config.preferred_job_type and job_listing.job_type:
        if user_config.preferred_job_type.lower() in job_listing.job_type.lower():
            score += weights['job_type']

    return min(100.0, max(0.0, score))  # Ensure score is between 0-100


def should_apply_to_job(job_listing, user_config, user_skills, threshold=70.0):
    """
    Determine if we should apply to this job
    Returns (should_apply: bool, match_score: float, reasons: list)
    """
    match_score = calculate_match_score(job_listing, user_config, user_skills)

    reasons = []

    if match_score >= threshold:
        if match_score >= 90:
            reasons.append("Excellent match for your skills and preferences")
        elif match_score >= 80:
            reasons.append("Very good match for your profile")
        else:
            reasons.append("Good match for your criteria")

        return True, match_score, reasons
    else:
        if match_score < 50:
            reasons.append("Low match score - job doesn't align well with preferences")
        else:
            reasons.append("Below threshold - consider adjusting search criteria")

        return False, match_score, reasons
