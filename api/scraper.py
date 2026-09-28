from fastapi import APIRouter, HTTPException
from utils.helpers import load_json, get_timestamp, log_event
import sys

# Module reload marker
print(f"SCRAPER_MODULE_LOADED: {sys.version}", file=sys.stderr)


router = APIRouter(prefix="/api/v1/scraper")


@router.get("/status")
async def get_scraper_status():
    """Get scraper configuration status"""
    config_path = "data/scraper_configs.json"
    config = load_json(config_path)
    
    return {
        "status": "active",
        "config": config,
        "timestamp": get_timestamp()
    }


@router.get("/config")
async def get_scraper_config():
    """Get scraper configuration"""
    config_path = "data/scraper_configs.json"
    config = load_json(config_path)
    
    return {"config": config}


@router.post("/config")
async def update_scraper_config(config: dict):
    """Update scraper configuration"""
    config_path = "data/scraper_configs.json"
    save_json(config_path, {"config": config})
    
    return {"message": "Configuration updated"}


@router.post("/scrape")
async def scrape_jobs(source: str = "seek"):
    """Scrape jobs from specified source"""
    import sys
    import os
    from scrapers import seek, linkedin, indeed, medical_boards
    
    try:
        scraper_map = {
            "seek": seek.SEEKScraper,
            "linkedin": linkedin.LinkedInScraper,
            "indeed": indeed.IndeedScraper,
            "medical_boards": medical_boards.MedicalBoardsScraper
        }
        
        if source not in scraper_map:
            raise ValueError(f"Unknown scraper source: {source}")
        
        ScraperClass = scraper_map[source]
        scraper = ScraperClass()
        jobs = await scraper.scrape()
        
        log_event("jobs_scraped", {"source": source, "count": len(jobs)})
        
        return {"source": source, "jobs": jobs, "count": len(jobs)}
    except Exception as e:
        log_event("scrape_error", {"source": source, "error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs")
async def get_scraped_jobs(source: str = "seek"):
    """Get recently scraped jobs from a source"""
    import sys
    import os
    from scrapers import seek, linkedin, indeed, medical_boards
    
    try:
        scraper_map = {
            "seek": seek.SEEKScraper,
            "linkedin": linkedin.LinkedInScraper,
            "indeed": indeed.IndeedScraper,
            "medical_boards": medical_boards.MedicalBoardsScraper
        }
        
        if source not in scraper_map:
            raise ValueError(f"Unknown scraper source: {source}")
        
        ScraperClass = scraper_map[source]
        scraper = ScraperClass()
        jobs = scraper.scrape()
        
        return {"source": source, "jobs": jobs, "count": len(jobs)}
    except Exception as e:
        log_event("get_scraped_jobs_error", {"source": source, "error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))
