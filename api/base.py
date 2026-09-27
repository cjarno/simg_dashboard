from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List, Dict
import os
import json
from datetime import datetime
from utils.helpers import load_json, save_json, get_timestamp, log_event


router = APIRouter(prefix="/api/v1")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": get_timestamp()}


@router.get("/status")
async def get_status():
    """Get application status and stats"""
    jobs_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'jobs.json')
    favorites_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'favorites.json')
    
    jobs = load_json(jobs_path)
    favorites = load_json(favorites_path)
    
    return {
        "status": "running",
        "jobs_count": len(jobs.get('jobs', [])),
        "favorites_count": len(favorites.get('favorites', [])),
        "timestamp": get_timestamp()
    }


@router.get("/logs")
async def get_logs():
    """Get application logs"""
    log_path = os.path.join(os.path.dirname(__file__), '..', '..', 'logs', 'app.log')
    logs = load_json(log_path)
    
    return {
        "app": logs.get('app'),
        "version": logs.get('version'),
        "started": logs.get('started'),
        "last_log": logs.get('logs', [])[-1] if logs.get('logs') else None
    }
