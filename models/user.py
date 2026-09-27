from pydantic import BaseModel, Field
from typing import List, Optional


class UserPreferences(BaseModel):
    """User preferences model - SIMG Report 1 criteria"""
    age_range: dict = Field(default={"min": 18, "max": 60})
    gender: Optional[str] = None
    medical_degree: Optional[str] = None
    years_experience: dict = Field(default={"min": 0, "max": 30})
    country_of_birth: Optional[str] = None
    country_of_practice: Optional[str] = None
    subspecialty_interest: Optional[str] = None
    academic_qualifications: List[str] = Field(default_factory=list)
    publications: Optional[str] = None
    research_experience: Optional[str] = None
    language_skills: List[str] = Field(default_factory=list)
    visa_status: Optional[str] = None
    relocation_willing: Optional[bool] = None
    salary_expectations: Optional[float] = None
    job_type: Optional[str] = None


class UserPreferencesUpdate(BaseModel):
    """User preferences update request"""
    age_range: Optional[dict] = None
    gender: Optional[str] = None
    medical_degree: Optional[str] = None
    years_experience: Optional[dict] = None
    country_of_birth: Optional[str] = None
    country_of_practice: Optional[str] = None
    subspecialty_interest: Optional[str] = None
    academic_qualifications: Optional[List[str]] = None
    publications: Optional[str] = None
    research_experience: Optional[str] = None
    language_skills: Optional[List[str]] = None
    visa_status: Optional[str] = None
    relocation_willing: Optional[bool] = None
    salary_expectations: Optional[float] = None
    job_type: Optional[str] = None
