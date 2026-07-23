"""
Simple In-Memory Cache for AI Insights
Independent caching system
"""

from datetime import datetime, timedelta
from typing import Optional
import hashlib
import json


class InsightCache:
    def __init__(self, ttl_hours: int = 24):
        self.cache = {}
        self.ttl = timedelta(hours=ttl_hours)
    
    def get_key(self, data: dict) -> str:
        """Generate cache key from analytics data"""
        try:
            return hashlib.md5(
                json.dumps(data, sort_keys=True).encode()
            ).hexdigest()
        except Exception:
            return None
    
    def get(self, key: str) -> Optional[dict]:
        """Get cached value if not expired"""
        if not key or key not in self.cache:
            return None
        
        value, timestamp = self.cache[key]
        if datetime.now() - timestamp < self.ttl:
            return value
        
        del self.cache[key]
        return None
    
    def set(self, key: str, value: dict):
        """Store in cache with timestamp"""
        if key:
            self.cache[key] = (value, datetime.now())
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()


# Global instance
insights_cache = InsightCache(ttl_hours=24)
