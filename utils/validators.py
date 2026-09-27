from typing import Dict, Any, Optional


def validate_job_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate job data"""
    required_fields = ['title', 'company', 'location', 'url', 'source']
    
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate URL
    if not data.get('url', '').startswith(('http://', 'https://')):
        data['url'] = 'https://' + data['url']
    
    # Validate posted date
    if data.get('posted_date'):
        from datetime import datetime
        try:
            datetime.fromisoformat(data['posted_date'].replace('Z', '+00:00'))
        except ValueError:
            data['posted_date'] = datetime.utcnow().isoformat() + 'Z'
    
    return data
