from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api import base_router, jobs_router, favorites_router, scraper_router
from utils.helpers import log_event, get_timestamp
import os


app = FastAPI(
    title="SIMG Dashboard API",
    description="Job matching platform for ANZCA candidates",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(base_router)
app.include_router(jobs_router)
app.include_router(favorites_router)
app.include_router(scraper_router)

# Mount static files directory
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "SIMG Dashboard",
        "version": "0.1.0",
        "description": "Job matching platform for ANZCA candidates",
        "docs": "/docs",
        "status": "/api/v1/health",
        "jobs": "/api/v1/jobs",
        "favorites": "/api/v1/favorites",
        "scraper": "/api/v1/scraper",
        "timestamp": get_timestamp()
    }

@app.get("/api/v1/info")
async def get_info():
    """Get application information"""
    return {
        "name": "SIMG Dashboard",
        "version": "0.1.0",
        "description": "Job matching platform for ANZCA candidates",
        "features": [
            "SIMG Report 1 filtering",
            "Multiple job board scraping",
            "Favorites system",
            "Dark mode UI",
            "State persistence"
        ]
    }

@app.get("/api/v1/logs")
async def get_logs():
    """Get application logs"""
    log_path = os.path.join(os.path.dirname(__file__), "logs", "app.log")
    from utils.helpers import load_json
    logs = load_json(log_path)
    return logs

# Health check endpoint
@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    log_event("app_started", {"version": "0.1.0"})
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
