from pydantic import BaseModel, Field
from typing import Optional


class Favorite(BaseModel):
    """Favorite job model"""
    id: str = Field(default_factory=lambda: f"fav_{id('uuid')}")
    job_id: str
    job_title: str
    job_url: str
    added_at: str = None


class FavoriteCreate(BaseModel):
    """Favorite creation request"""
    job_id: str
    job_title: str
    job_url: str


class FavoriteUpdate(BaseModel):
    """Favorite update request"""
    job_title: Optional[str] = None
    job_url: Optional[str] = None
