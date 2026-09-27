from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class JobFilter(BaseModel):
    """SIMG Report 1 Criteria Filter"""
    age_min: Optional[int] = Field(None, ge=18, le=60)
    age_max: Optional[int] = Field(None, ge=18, le=60)
    gender: Optional[str] = None
    medical_degree: Optional[str] = None
    years_experience_min: Optional[int] = Field(None, ge=0, le=30)
    years_experience_max: Optional[int] = Field(None, ge=0, le=30)
    country_of_birth: Optional[str] = None
    country_of_practice: Optional[str] = None
    subspecialty_interest: Optional[str] = None
    academic_qualifications: Optional[List[str]] = None
    publications: Optional[str] = None
    research_experience: Optional[str] = None
    language_skills: Optional[List[str]] = None
    visa_status: Optional[str] = None
    relocation_willing: Optional[bool] = None
    salary_expectations_min: Optional[float] = None
    salary_expectations_max: Optional[float] = None
    job_type: Optional[str] = None
    keywords: Optional[List[str]] = None


class Job(BaseModel):
    """Job posting model"""
    id: str = Field(default_factory=lambda: f"job_{id('uuid')}")
    title: str
    company: str
    location: str
    url: str
    source: str
    posted_date: str
    job_type: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    tags: List[str] = []
    scraped_at: str = None


class JobCreate(BaseModel):
    """Job creation request"""
    title: str
    company: str
    location: str
    url: str
    source: str
    posted_date: Optional[str] = None
    job_type: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class JobUpdate(BaseModel):
    """Job update request"""
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    tags: Optional[List[str]] = None
