from fastapi import APIRouter, HTTPException, Query, Request
from typing import List, Optional, Dict
from utils.helpers import load_json, save_json, get_timestamp, log_event
from models.favorite import Favorite, FavoriteCreate, FavoriteUpdate


router = APIRouter(prefix="/api/v1/favorites")


def load_favorites() -> List[Dict]:
    favorites_path = "data/favorites.json"
    return load_json(favorites_path).get('favorites', [])


def save_favorites(favorites: List[Dict]) -> None:
    favorites_path = "data/favorites.json"
    save_json(favorites_path, {"favorites": favorites})


@router.get("/")
async def list_favorites(
    page: int = 1,
    page_size: int = 20,
    request: Request = None
):
    """List all favorite jobs"""
    try:
        favorites = load_favorites()
        
        start = (page - 1) * page_size
        end = start + page_size
        paginated = favorites[start:end]
        
        return {
            "favorites": paginated,
            "total": len(favorites),
            "page": page,
            "page_size": page_size,
            "total_pages": (len(favorites) + page_size - 1) // page_size
        }
    except Exception as e:
        log_event("list_favorites_error", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{favorite_id}")
async def get_favorite(favorite_id: str, request: Request = None):
    """Get a specific favorite by ID"""
    try:
        favorites = load_favorites()
        favorite = next((f for f in favorites if f.get('id') == favorite_id), None)
        
        if not favorite:
            raise HTTPException(status_code=404, detail="Favorite not found")
        
        return favorite
    except HTTPException:
        raise
    except Exception as e:
        log_event("get_favorite_error", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", status_code=201)
async def create_favorite(favorite: FavoriteCreate, request: Request = None):
    """Add a job to favorites"""
    try:
        favorites = load_favorites()
        
        # Check if already exists
        if any(f.get('job_id') == favorite.job_id for f in favorites):
            raise HTTPException(status_code=400, detail="Job already in favorites")
        
        favorite_dict = favorite.model_dump()
        favorite_dict['added_at'] = get_timestamp()
        
        favorites.append(favorite_dict)
        save_favorites(favorites)
        
        log_event("favorite_created", {"favorite_id": favorite_dict['id'], "job_id": favorite_dict['job_id']})
        
        return favorite_dict
    except HTTPException:
        raise
    except Exception as e:
        log_event("create_favorite_error", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{favorite_id}")
async def update_favorite(favorite_id: str, favorite: FavoriteUpdate, request: Request = None):
    """Update a favorite"""
    try:
        favorites = load_favorites()
        index = next((i for i, f in enumerate(favorites) if f.get('id') == favorite_id), None)
        
        if index is None:
            raise HTTPException(status_code=404, detail="Favorite not found")
        
        for key, value in favorite.model_dump().items():
            if value is not None:
                favorites[index][key] = value
        
        save_favorites(favorites)
        
        log_event("favorite_updated", {"favorite_id": favorite_id})
        
        return favorites[index]
    except HTTPException:
        raise
    except Exception as e:
        log_event("update_favorite_error", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{favorite_id}")
async def delete_favorite(favorite_id: str, request: Request = None):
    """Remove a job from favorites"""
    try:
        favorites = load_favorites()
        favorites = [f for f in favorites if f.get('id') != favorite_id]
        save_favorites(favorites)
        
        log_event("favorite_deleted", {"favorite_id": favorite_id})
        
        return {"message": "Favorite removed successfully"}
    except Exception as e:
        log_event("delete_favorite_error", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/job/{job_id}")
async def check_favorite(job_id: str, request: Request = None):
    """Check if a job is favorited"""
    try:
        favorites = load_favorites()
        is_favorited = any(f.get('job_id') == job_id for f in favorites)
        
        return {
            "job_id": job_id,
            "is_favorited": is_favorited
        }
    except Exception as e:
        log_event("check_favorite_error", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))
