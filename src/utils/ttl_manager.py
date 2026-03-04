#!/usr/bin/env python3
"""
TTL Manager - Session-Based Privacy Component
Manages DynamoDB Time-To-Live attributes for automatic data deletion
"""

import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TTLManager:
    """Manage TTL for user sessions with automatic data deletion"""
    
    # Session duration: 3 hours in seconds
    SESSION_DURATION_SECONDS = 3 * 3600  # 10800 seconds
    
    @staticmethod
    def calculate_expiry_time() -> int:
        """
        Calculate expiry time for new records
        
        Returns:
            int: Unix timestamp for expiry (current time + 3 hours)
        """
        expiry_time = int(time.time()) + TTLManager.SESSION_DURATION_SECONDS
        logger.debug(f"Calculated expiry time: {expiry_time} (3 hours from now)")
        return expiry_time
    
    @staticmethod
    def extend_session(current_expiry_time: Optional[int] = None) -> int:
        """
        Extend session by resetting TTL to 3 hours from now
        
        This is called on every user interaction to keep the session alive.
        The current_expiry_time parameter is ignored - we always reset to 3 hours from now.
        
        Args:
            current_expiry_time: Existing expiry time (ignored, always reset)
        
        Returns:
            int: New expiry time (current time + 3 hours)
        """
        new_expiry = TTLManager.calculate_expiry_time()
        
        if current_expiry_time:
            logger.debug(f"Extended session from {current_expiry_time} to {new_expiry}")
        else:
            logger.debug(f"Set new session expiry: {new_expiry}")
        
        return new_expiry
    
    @staticmethod
    def is_expired(expiry_time: int) -> bool:
        """
        Check if a record has expired
        
        Args:
            expiry_time: Unix timestamp
        
        Returns:
            bool: True if expired (current time > expiry time)
        """
        current_time = int(time.time())
        expired = current_time > expiry_time
        
        if expired:
            logger.debug(f"Record expired: {expiry_time} < {current_time}")
        
        return expired
    
    @staticmethod
    def get_time_until_expiry(expiry_time: int) -> int:
        """
        Get seconds until expiry
        
        Args:
            expiry_time: Unix timestamp
        
        Returns:
            int: Seconds until expiry (negative if already expired)
        """
        current_time = int(time.time())
        seconds_remaining = expiry_time - current_time
        
        return seconds_remaining
    
    @staticmethod
    def format_expiry_time(expiry_time: int) -> str:
        """
        Format expiry time as human-readable string
        
        Args:
            expiry_time: Unix timestamp
        
        Returns:
            str: Formatted datetime string
        """
        from datetime import datetime
        dt = datetime.fromtimestamp(expiry_time)
        return dt.strftime('%Y-%m-%d %H:%M:%S')


# Module-level instance for reuse across Lambda invocations
_ttl_manager_instance = None


def get_ttl_manager() -> TTLManager:
    """
    Get or create TTL manager instance (singleton pattern for Lambda)
    
    Returns:
        TTLManager: Reusable manager instance
    """
    global _ttl_manager_instance
    if _ttl_manager_instance is None:
        _ttl_manager_instance = TTLManager()
    return _ttl_manager_instance
