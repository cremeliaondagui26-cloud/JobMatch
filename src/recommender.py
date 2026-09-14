from __future__ import annotations

from collections.abc import Sequence


def rank_matches(candidate_skills: Sequence[str], job_skills: Sequence[str]) -> float:
    """Score a candidate/job pair with a simple overlap ratio."""
    candidate_set = {skill.strip().lower() for skill in candidate_skills if skill}
    job_set = {skill.strip().lower() for skill in job_skills if skill}

    if not job_set:
        return 0.0

    return len(candidate_set & job_set) / len(job_set)
