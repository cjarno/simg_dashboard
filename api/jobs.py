from fastapi import APIRouter, HTTPException, Query, Request
from typing import List, Optional, Dict
from utils.helpers import load_json, save_json, get_timestamp, log_event
from utils.filters import filter_jobs_by_criteria
from models.job import Job, JobCreate, JobUpdate, JobFilter


router = APIRouter(prefix="/api/v1/jobs")


def load_jobs() -> List[Dict]:
    jobs_path = "data/jobs.json"
    return load_json(jobs_path).get('jobs', [])


def save_jobs(jobs: List[Dict]) -> None:
    jobs_path = "data/jobs.json"
    save_json(jobs_path, {"jobs": jobs})


def load_favorites() -> List[Dict]:
    favorites_path = "data/favorites.json"
    return load_json(favorites_path).get('favorites', [])


def save_favorites(favorites: List[Dict]) -> None:
    favorites_path = "data/favorites.json"
    save_json(favorites_path, {"favorites": favorites})


@router.get("/")
async def list_jobs(
    page: int = 1,
    page_size: int = 20,
    job_type: Optional[str] = None,
    keywords: Optional[str] = None,
    request: Request = None
):
    """List all jobs with pagination"""
    try:
        jobs = load_jobs()
        
        # Filter by job type
        if job_type:
            jobs = [j for j in jobs if j.get('job_type') == job_type]
        
        # Filter by keywords
        if keywords:
            kw_lower = keywords.lower()
            jobs = [j for j in jobs if kw_lower in j.get('title', '').lower() or kw_lower in j.get('description', '').lower()]
        
        # Pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated = jobs[start:end]
        
        return {
            "jobs": paginated,
            "total": len(jobs),
            "page": page,
            "page_size": page_size,
            "total_pages": (len(jobs) + page_size - 1) // page_size
        }
    except Exception as e:
        log_event("list_jobs_error", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}")
async def get_job(job_id: str, request: Request = None):
    """Get a specific job by ID"""
    try:
        jobs = load_jobs()
        job = next((j for j in jobs if j.get('id') == job_id), None)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return job
    except HTTPException:
        raise
    except Exception as e:
        log_event("get_job_error", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", status_code=201)
async def create_job(job: JobCreate, request: Request = None):
    """Create a new job"""
    try:
        jobs = load_jobs()
        job_dict = job.model_dump()
        job_dict['scraped_at'] = get_timestamp()
        
        jobs.append(job_dict)
        save_jobs(jobs)
        
        log_event("job_created", {"job_id": job_dict['id'], "title": job_dict['title']})
        
        return job_dict
    except Exception as e:
        log_event("create_job_error", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{job_id}")
async def update_job(job_id: str, job: JobUpdate, request: Request = None):
    """Update a job"""
    try:
        jobs = load_jobs()
        index = next((i for i, j in enumerate(jobs) if j.get('id') == job_id), None)
        
        if index is None:
            raise HTTPException(status_code=404, detail="Job not found")
        
        for key, value in job.model_dump().items():
            if value is not None:
                jobs[index][key] = value
        
        save_jobs(jobs)
        
        log_event("job_updated", {"job_id": job_id})
        
        return jobs[index]
    except HTTPException:
        raise
    except Exception as e:
        log_event("update_job_error", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{job_id}")
async def delete_job(job_id: str, request: Request = None):
    """Delete a job"""
    try:
        jobs = load_jobs()
        jobs = [j for j in jobs if j.get('id') != job_id]
        save_jobs(jobs)
        
        log_event("job_deleted", {"job_id": job_id})
        
        return {"message": "Job deleted successfully"}
    except Exception as e:
        log_event("delete_job_error", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scrape", tags=["scraping"])
async def scrape_jobs(request: Request = None):
    """Scrape jobs from multiple job boards"""
    from scrapers import seek, linkedin, indeed, medical_boards
    import asyncio
    
    try:
        log_event("scrape_started")
        
        async def scrape_from_source(source, scraper):
            """Scrape from a single source"""
            try:
                jobs = await scraper.scrape()
                log_event(f"scrape_{source}", {"jobs_found": len(jobs)})
                return jobs
            except Exception as e:
                log_event(f"scrape_{source}_error", {"error": str(e)})
                return []
        
        tasks = [
            scrape_from_source("seek", seek.SEEKScraper()),
            scrape_from_source("linkedin", linkedin.LinkedInScraper()),
            scrape_from_source("indeed", indeed.IndeedScraper()),
            scrape_from_source("medical_boards", medical_boards.MedicalBoardsScraper())
        ]
        
        jobs = await asyncio.gather(*tasks)
        jobs = [job for source_jobs in jobs for job in source_jobs]
        
        # Remove duplicates
        seen = set()
        unique_jobs = []
        for job in jobs:
            job_key = (job.get('title'), job.get('url'))
            if job_key not in seen:
                seen.add(job_key)
                unique_jobs.append(job)
        
        # Save jobs
        current_jobs = load_jobs()
        current_jobs.extend(unique_jobs)
        save_jobs(current_jobs)
        
        log_event("scrape_completed", {"total_jobs": len(unique_jobs)})
        
        return {
            "message": "Jobs scraped successfully",
            "total_scraped": len(unique_jobs),
            "by_source": {
                "seek": len([j for j in jobs if j.get('source') == 'seek']),
                "linkedin": len([j for j in jobs if j.get('source') == 'linkedin']),
                "indeed": len([j for j in jobs if j.get('source') == 'indeed']),
                "medical_boards": len([j for j in jobs if j.get('source') == 'medical_boards'])
            }
        }
    except Exception as e:
        log_event("scrape_error", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))
