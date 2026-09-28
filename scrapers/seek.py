import asyncio
import time
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from requests import Session
from utils.helpers import get_timestamp, log_event
from scrapers.base_scraper import BaseScraper

class SEEKScraper(BaseScraper):
    """SEEK Australia job scraper with real web scraping"""
    
    def __init__(self):
        super().__init__("seek")
        self.base_url = "https://www.seek.com.au"
        self.search_terms = ["anaesthetist", "anaesthesia", "critical care", "anaesthesia specialist"]
        self.session = Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        })
    
    async def scrape(self, limit: int = 20, delay: float = 3.0) -> List[Dict]:
        """Scrape jobs from SEEK with real web scraping"""
        jobs = []
        all_jobs = []
        
        try:
            # Use the first search term
            search_term = self.search_terms[0]
            search_url = f"{self.base_url}/j/search?q={search_term}"
            
            log_event("scraper_started", {
                "source": self.source,
                "url": search_url,
                "limit": limit
            })
            
            # Retry logic with exponential backoff
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.session.get(search_url, timeout=30)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.text, 'lxml')
                    job_listings = soup.find_all('div', class_='job-row')
                    
                    for idx, job_elem in enumerate(job_listings[:limit]):
                        try:
                            job_data = await self._parse_job(job_elem, search_term)
                            if job_data:
                                all_jobs.append(job_data)
                        except Exception as e:
                            log_event("scraper_job_parse_error", {
                                "job_index": idx,
                                "error": str(e)
                            })
                            continue
                    
                    # Check if we got any results
                    if len(all_jobs) > 0:
                        break
                    
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)
                        log_event("scraper_rate_limit", {
                            "attempt": attempt + 1,
                            "wait_time": wait_time
                        })
                        await asyncio.sleep(wait_time)
                        
                except Exception as e:
                    log_event("scraper_request_error", {
                        "attempt": attempt + 1,
                        "error": str(e)
                    })
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)
                        await asyncio.sleep(wait_time)
                    else:
                        raise
            
            # Add unique jobs
            seen_ids = set()
            for job in all_jobs:
                if job['id'] not in seen_ids:
                    jobs.append(job)
                    seen_ids.add(job['id'])
            
            log_event("scraper_completed", {
                "source": self.source,
                "jobs_count": len(jobs)
            })
            
            return jobs
            
        except Exception as e:
            log_event("scraper_fatal_error", {
                "source": self.source,
                "error": str(e)
            })
            return []

    async def _parse_job(self, job_elem, search_term: str) -> Optional[Dict]:
        """Parse a single job listing from SEEK"""
        try:
            # Extract job details from SEEK's HTML structure
            title_elem = job_elem.find('h2', class_='job-title')
            company_elem = job_elem.find('a', class_='company-name')
            location_elem = job_elem.find('span', class_='location')
            
            title = title_elem.get_text(strip=True) if title_elem else f"{search_term} Position"
            company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
            location = location_elem.get_text(strip=True) if location_elem else "Australia"
            
            # Get job URL
            job_url = job_elem.find('a')
            if job_url and 'href' in job_url.attrs:
                job_url = job_url['href']
            else:
                job_url = f"{self.base_url}/j/search?q={search_term}"
            
            # Extract salary if available
            salary_elem = job_elem.find('span', class_='salary')
            salary_min = salary_elem.get_text(strip=True) if salary_elem else None
            salary_max = None
            
            # Extract job type
            job_type_elem = job_elem.find('span', class_='job-type')
            job_type = job_type_elem.get_text(strip=True) if job_type_elem else "Full-time"
            
            # Extract requirements
            requirements = []
            req_elem = job_elem.find('ul', class_='requirements')
            if req_elem:
                for li in req_elem.find_all('li'):
                    requirements.append(li.get_text(strip=True))
            
            # Generate tags from job title
            tags = self._extract_tags(title)
            
            return {
                "id": self._generate_id(title, f"seek_{len(jobs) + 1}"),
                "title": title,
                "company": company,
                "location": location,
                "url": job_url,
                "source": "seek",
                "posted_date": get_timestamp(),
                "job_type": job_type,
                "salary_min": float(salary_min.replace('$', '')) if salary_min else None,
                "salary_max": float(salary_max.replace('$', '')) if salary_max else None,
                "description": f"Seeking experienced {search_term} for {location}",
                "requirements": requirements if requirements else ["Standard ANZCA requirements"],
                "tags": tags
            }
            
        except Exception as e:
            log_event("scraper_parse_error", {
                "error": str(e),
                "search_term": search_term
            })
            return None

    def _extract_tags(self, title: str) -> List[str]:
        """Extract relevant tags from job title"""
        tags = []
        title_lower = title.lower()
        
        tag_keywords = {
            "anaesthesia": "anaesthesia",
            "critical": "critical care",
            "sydney": "sydney",
            "melbourne": "melbourne",
            "brisbane": "brisbane",
            "perth": "perth",
            "adelaide": "adelaide",
            "hospital": "hospital",
            "health": "healthcare",
            "public": "public sector",
            "private": "private practice",
            "franzca": "franzca",
            "senior": "senior",
            "consultant": "consultant",
            "registrar": "registrar",
            "fellowship": "fellowship"
        }
        
        for keyword, tag in tag_keywords.items():
            if keyword in title_lower:
                tags.append(tag)
        
        return tags if tags else ["anaesthesia"]

    def close(self):
        """Close the session"""
        self.session.close()
