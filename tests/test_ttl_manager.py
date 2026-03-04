#!/usr/bin/env python3
"""
Unit tests for TTL Manager component
"""

import pytest
import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils.ttl_manager import TTLManager, get_ttl_manager


class TestTTLManager:
    """Test TTL Manager functionality"""
    
    def test_calculate_expiry_time(self):
        """Test expiry time calculation"""
        current_time = int(time.time())
        expiry_time = TTLManager.calculate_expiry_time()
        
        # Should be approximately 3 hours (10800 seconds) from now
        expected_expiry = current_time + (3 * 3600)
        
        # Allow 2 seconds tolerance for test execution time
        assert abs(expiry_time - expected_expiry) < 2
    
    def test_expiry_time_in_future(self):
        """Test that expiry time is in the future"""
        current_time = int(time.time())
        expiry_time = TTLManager.calculate_expiry_time()
        
        assert expiry_time > current_time
    
    def test_extend_session(self):
        """Test session extension"""
        old_expiry = int(time.time()) + 1800  # 30 minutes from now
        new_expiry = TTLManager.extend_session(old_expiry)
        
        # New expiry should be ~3 hours from now
        current_time = int(time.time())
        expected_expiry = current_time + (3 * 3600)
        
        assert abs(new_expiry - expected_expiry) < 2
        assert new_expiry > old_expiry  # Should be extended
    
    def test_extend_session_without_current(self):
        """Test session extension without current expiry time"""
        new_expiry = TTLManager.extend_session()
        
        current_time = int(time.time())
        expected_expiry = current_time + (3 * 3600)
        
        assert abs(new_expiry - expected_expiry) < 2
    
    def test_is_expired_true(self):
        """Test expired record detection"""
        # Create expiry time in the past
        past_expiry = int(time.time()) - 3600  # 1 hour ago
        
        assert TTLManager.is_expired(past_expiry) is True
    
    def test_is_expired_false(self):
        """Test non-expired record detection"""
        # Create expiry time in the future
        future_expiry = int(time.time()) + 3600  # 1 hour from now
        
        assert TTLManager.is_expired(future_expiry) is False
    
    def test_get_time_until_expiry_positive(self):
        """Test time until expiry for future expiry"""
        future_expiry = int(time.time()) + 1800  # 30 minutes from now
        
        seconds_remaining = TTLManager.get_time_until_expiry(future_expiry)
        
        # Should be approximately 1800 seconds
        assert 1798 <= seconds_remaining <= 1800
    
    def test_get_time_until_expiry_negative(self):
        """Test time until expiry for past expiry"""
        past_expiry = int(time.time()) - 1800  # 30 minutes ago
        
        seconds_remaining = TTLManager.get_time_until_expiry(past_expiry)
        
        # Should be negative
        assert seconds_remaining < 0
        assert -1800 <= seconds_remaining <= -1798
    
    def test_format_expiry_time(self):
        """Test expiry time formatting"""
        expiry_time = 1704067200  # 2024-01-01 00:00:00
        
        formatted = TTLManager.format_expiry_time(expiry_time)
        
        assert isinstance(formatted, str)
        assert '2024' in formatted or '2023' in formatted  # Depends on timezone
    
    def test_session_duration_constant(self):
        """Test that session duration is 3 hours"""
        assert TTLManager.SESSION_DURATION_SECONDS == 10800
        assert TTLManager.SESSION_DURATION_SECONDS == 3 * 3600
    
    def test_get_ttl_manager_singleton(self):
        """Test that get_ttl_manager returns singleton instance"""
        manager1 = get_ttl_manager()
        manager2 = get_ttl_manager()
        
        assert manager1 is manager2  # Same instance


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
