from fastapi import APIRouter
from utils.helpers import load_json, get_timestamp, log_event


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
