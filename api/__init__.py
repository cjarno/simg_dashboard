from .base import router as base_router
from .jobs import router as jobs_router
from .favorites import router as favorites_router
from .scraper import router as scraper_router

__all__ = ["base_router", "jobs_router", "favorites_router", "scraper_router"]
