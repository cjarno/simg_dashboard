from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import datetime
from utils.helpers import get_timestamp


class BaseScraper(ABC):
    """Base class for job board scrapers"""
    
    def __init__(self, name: str = "base"):
        self.name = name
        self.enabled = True
    
    @abstractmethod
    async def scrape(self) -> List[Dict]:
        """Scrape jobs from this source"""
        pass
    
    async def _parse_date(self, date_str: str) -> str:
        """Parse date string to ISO format"""
        if not date_str:
            return get_timestamp()
        
        try:
            # Try various date formats
            for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y"]:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.isoformat() + 'Z'
                except ValueError:
                    continue
            # If all fail, use current timestamp
            return get_timestamp()
        except Exception:
            return get_timestamp()
    
    def _generate_id(self, title: str, url: str) -> str:
        """Generate a unique ID from title and URL"""
        import hashlib
        content = f"{title}{url}"
        return f"{self.name}_{hashlib.md5(content.encode()).hexdigest()[:8]}"
