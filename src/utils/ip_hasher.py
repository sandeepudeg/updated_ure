#!/usr/bin/env python3
"""
IP Address Hasher - Privacy Protection Component
Hashes IP addresses using SHA-256 with salt to protect user location privacy
"""

import hashlib
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class IPAddressHasher:
    """Hash IP addresses for privacy protection"""
    
    def __init__(self):
        """Initialize with salt from environment variable"""
        self.salt = os.environ.get('IP_HASH_SALT', 'default_salt_change_me')
        
        if self.salt == 'default_salt_change_me':
            logger.warning("Using default IP hash salt - should be changed in production")
    
    def hash_ip(self, ip_address: str) -> Optional[str]:
        """
        Hash IP address using SHA-256 with salt
        
        Args:
            ip_address: IPv4 or IPv6 address
        
        Returns:
            str: Hex-encoded SHA-256 hash, or None if ip_address is empty
        """
        if not ip_address:
            return None
        
        # Combine IP with salt
        salted_ip = f"{ip_address}{self.salt}"
        
        # Hash with SHA-256
        hash_object = hashlib.sha256(salted_ip.encode('utf-8'))
        hashed_ip = hash_object.hexdigest()
        
        logger.debug(f"Hashed IP address (first 8 chars): {hashed_ip[:8]}...")
        
        return hashed_ip
    
    def extract_ip_from_event(self, event: Dict[str, Any]) -> Optional[str]:
        """
        Extract source IP from API Gateway event
        
        Args:
            event: Lambda event from API Gateway
        
        Returns:
            str: Source IP address or None
        """
        # API Gateway includes source IP in requestContext
        request_context = event.get('requestContext', {})
        identity = request_context.get('identity', {})
        source_ip = identity.get('sourceIp')
        
        # Fallback to headers if not in requestContext
        if not source_ip:
            headers = event.get('headers', {})
            # Check X-Forwarded-For header (CloudFront)
            x_forwarded_for = headers.get('X-Forwarded-For', '')
            if x_forwarded_for:
                # Take first IP in the chain
                source_ip = x_forwarded_for.split(',')[0].strip()
        
        if source_ip:
            logger.debug(f"Extracted IP address: {source_ip[:8]}...")
        else:
            logger.warning("Could not extract IP address from event")
        
        return source_ip if source_ip else None
    
    def extract_and_hash_ip(self, event: Dict[str, Any]) -> Optional[str]:
        """
        Extract IP from event and hash it (convenience method)
        
        Args:
            event: Lambda event from API Gateway
        
        Returns:
            str: Hashed IP address or None
        """
        ip_address = self.extract_ip_from_event(event)
        if ip_address:
            return self.hash_ip(ip_address)
        return None


# Module-level instance for reuse across Lambda invocations
_ip_hasher_instance = None


def get_ip_hasher() -> IPAddressHasher:
    """
    Get or create IP hasher instance (singleton pattern for Lambda)
    
    Returns:
        IPAddressHasher: Reusable hasher instance
    """
    global _ip_hasher_instance
    if _ip_hasher_instance is None:
        _ip_hasher_instance = IPAddressHasher()
    return _ip_hasher_instance
