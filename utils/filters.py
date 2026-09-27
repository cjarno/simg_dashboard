from typing import List, Dict, Any, Optional
from models.job import Job, JobFilter


def filter_jobs_by_criteria(jobs: List[Dict], filter: JobFilter) -> List[Dict]:
    """Filter jobs by SIMG Report 1 criteria"""
    filtered = jobs
    
    if filter.age_min is not None:
        filtered = [j for j in filtered if j.get('age') and int(j['age']) >= filter.age_min]
    
    if filter.age_max is not None:
        filtered = [j for j in filtered if j.get('age') and int(j['age']) <= filter.age_max]
    
    if filter.gender is not None:
        filtered = [j for j in filtered if j.get('gender') == filter.gender]
    
    if filter.medical_degree is not None:
        filtered = [j for j in filtered if j.get('medical_degree') == filter.medical_degree]
    
    if filter.years_experience_min is not None:
        filtered = [j for j in filtered if j.get('years_experience') and int(j['years_experience']) >= filter.years_experience_min]
    
    if filter.years_experience_max is not None:
        filtered = [j for j in filtered if j.get('years_experience') and int(j['years_experience']) <= filter.years_experience_max]
    
    if filter.country_of_birth is not None:
        filtered = [j for j in filtered if j.get('country_of_birth') == filter.country_of_birth]
    
    if filter.country_of_practice is not None:
        filtered = [j for j in filtered if j.get('country_of_practice') == filter.country_of_practice]
    
    if filter.subspecialty_interest is not None:
        filtered = [j for j in filtered if j.get('subspecialty_interest') == filter.subspecialty_interest]
    
    if filter.job_type is not None:
        filtered = [j for j in filtered if j.get('job_type') == filter.job_type]
    
    if filter.keywords:
        filtered = [j for j in filtered if any(kw in j.get('title', '').lower() for kw in filter.keywords)]
    
    return filtered
