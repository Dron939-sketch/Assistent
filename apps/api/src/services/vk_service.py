"""
VK API service for parsing groups and pages
"""

import re
import json
from typing import Optional, Dict, Any, List
import httpx
import logging

from src.core.config import settings

logger = logging.getLogger(__name__)


class VKService:
    """Service for VK API interactions"""
    
    def __init__(self):
        self.api_version = settings.VK_API_VERSION
        self.access_token = settings.VK_SERVICE_KEY
        self.base_url = "https://api.vk.com/method/"
    
    def extract_group_id(self, url: str) -> Optional[str]:
        """
        Extract group ID from VK URL
        Supports:
        - https://vk.com/club123456
        - https://vk.com/public123456
        - https://vk.com/username
        - https://m.vk.com/...
        """
        patterns = [
            r'vk\.com/(club|public)?(\d+)',
            r'vk\.com/([a-zA-Z0-9_\.]+)',
            r'm\.vk\.com/(club|public)?(\d+)',
            r'm\.vk\.com/([a-zA-Z0-9_\.]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                if len(match.groups()) == 2:
                    # club123456 or public123456
                    return match.group(2)
                else:
                    # username
                    return match.group(1)
        
        return None
    
    async def get_group_info(self, group_id: str) -> Optional[Dict[str, Any]]:
        """Get VK group information"""
        params = {
            "group_id": group_id,
            "fields": "description,status,members_count,cover,counters,activity",
            "access_token": self.access_token,
            "v": self.api_version
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}groups.getById",
                    params=params,
                    timeout=30.0
                )
                data = response.json()
                
                if "error" in data:
                    logger.error(f"VK API error: {data['error']}")
                    return None
                
                groups = data.get("response", {}).get("groups", [])
                if groups:
                    return groups[0]
                
                return None
                
            except Exception as e:
                logger.error(f"Failed to fetch group info: {e}")
                return None
    
    async def get_wall_posts(
        self, 
        group_id: str, 
        count: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get wall posts from group"""
        params = {
            "owner_id": f"-{group_id}",
            "count": count,
            "offset": offset,
            "extended": 1,
            "access_token": self.access_token,
            "v": self.api_version
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}wall.get",
                    params=params,
                    timeout=30.0
                )
                data = response.json()
                
                if "error" in data:
                    logger.error(f"VK API error: {data['error']}")
                    return []
                
                items = data.get("response", {}).get("items", [])
                return items
                
            except Exception as e:
                logger.error(f"Failed to fetch wall posts: {e}")
                return []
    
    async def get_post_comments(
        self,
        group_id: str,
        post_id: int,
        count: int = 100
    ) -> List[Dict[str, Any]]:
        """Get comments for a specific post"""
        params = {
            "owner_id": f"-{group_id}",
            "post_id": post_id,
            "count": count,
            "extended": 1,
            "access_token": self.access_token,
            "v": self.api_version
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}wall.getComments",
                    params=params,
                    timeout=30.0
                )
                data = response.json()
                
                if "error" in data:
                    logger.error(f"VK API error: {data['error']}")
                    return []
                
                items = data.get("response", {}).get("items", [])
                return items
                
            except Exception as e:
                logger.error(f"Failed to fetch comments: {e}")
                return []
    
    async def get_pinned_post(self, group_id: str) -> Optional[Dict[str, Any]]:
        """Get pinned post from group wall"""
        params = {
            "owner_id": f"-{group_id}",
            "count": 1,
            "filter": "all",
            "access_token": self.access_token,
            "v": self.api_version
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}wall.get",
                    params=params,
                    timeout=30.0
                )
                data = response.json()
                
                if "error" in data:
                    return None
                
                items = data.get("response", {}).get("items", [])
                for item in items:
                    if item.get("is_pinned") == 1:
                        return item
                
                return None
                
            except Exception as e:
                logger.error(f"Failed to fetch pinned post: {e}")
                return None
