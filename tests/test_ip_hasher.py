#!/usr/bin/env python3
"""
Unit tests for IP Address Hasher component
"""

import pytest
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils.ip_hasher import IPAddressHasher, get_ip_hasher


class TestIPAddressHasher:
    """Test IP Address Hasher functionality"""
    
    def test_hash_ip_basic(self):
        """Test basic IP hashing"""
        hasher = IPAddressHasher()
        
        ip = "192.168.1.1"
        hashed = hasher.hash_ip(ip)
        
        assert hashed is not None
        assert len(hashed) == 64  # SHA-256 produces 64 hex characters
        assert isinstance(hashed, str)
    
    def test_hash_ip_deterministic(self):
        """Test that hashing the same IP produces the same result"""
        hasher = IPAddressHasher()
        
        ip = "10.0.0.1"
        hash1 = hasher.hash_ip(ip)
        hash2 = hasher.hash_ip(ip)
        
        assert hash1 == hash2
    
    def test_hash_ip_different_ips(self):
        """Test that different IPs produce different hashes"""
        hasher = IPAddressHasher()
        
        ip1 = "192.168.1.1"
        ip2 = "192.168.1.2"
        
        hash1 = hasher.hash_ip(ip1)
        hash2 = hasher.hash_ip(ip2)
        
        assert hash1 != hash2
    
    def test_hash_ip_empty(self):
        """Test hashing empty IP returns None"""
        hasher = IPAddressHasher()
        
        assert hasher.hash_ip("") is None
        assert hasher.hash_ip(None) is None
    
    def test_hash_ip_with_custom_salt(self):
        """Test hashing with custom salt"""
        # Set custom salt
        os.environ['IP_HASH_SALT'] = 'test_salt_12345'
        
        hasher = IPAddressHasher()
        ip = "192.168.1.1"
        hashed = hasher.hash_ip(ip)
        
        assert hashed is not None
        assert len(hashed) == 64
        
        # Clean up
        del os.environ['IP_HASH_SALT']
    
    def test_extract_ip_from_request_context(self):
        """Test IP extraction from API Gateway requestContext"""
        hasher = IPAddressHasher()
        
        event = {
            'requestContext': {
                'identity': {
                    'sourceIp': '203.0.113.1'
                }
            }
        }
        
        ip = hasher.extract_ip_from_event(event)
        assert ip == '203.0.113.1'
    
    def test_extract_ip_from_x_forwarded_for(self):
        """Test IP extraction from X-Forwarded-For header"""
        hasher = IPAddressHasher()
        
        event = {
            'headers': {
                'X-Forwarded-For': '203.0.113.1, 198.51.100.1'
            }
        }
        
        ip = hasher.extract_ip_from_event(event)
        assert ip == '203.0.113.1'  # Should take first IP
    
    def test_extract_ip_missing(self):
        """Test IP extraction when no IP is available"""
        hasher = IPAddressHasher()
        
        event = {}
        ip = hasher.extract_ip_from_event(event)
        
        assert ip is None
    
    def test_get_ip_hasher_singleton(self):
        """Test that get_ip_hasher returns singleton instance"""
        hasher1 = get_ip_hasher()
        hasher2 = get_ip_hasher()
        
        assert hasher1 is hasher2  # Same instance
    
    def test_extract_and_hash_ip(self):
        """Test convenience method that extracts and hashes in one call"""
        hasher = IPAddressHasher()
        
        event = {
            'requestContext': {
                'identity': {
                    'sourceIp': '192.168.1.100'
                }
            }
        }
        
        hashed_ip = hasher.extract_and_hash_ip(event)
        
        assert hashed_ip is not None, "Should return hashed IP"
        assert len(hashed_ip) == 64, "SHA-256 hash should be 64 hex chars"
        assert '192.168.1.100' not in hashed_ip, "Should not contain plaintext IP"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
