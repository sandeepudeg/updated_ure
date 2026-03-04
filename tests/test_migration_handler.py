#!/usr/bin/env python3
"""
Unit tests for Migration Handler
Tests legacy user migration detection and data migration logic
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError
from src.utils.migration_handler import (
    detect_migration_needed,
    is_legacy_user_id,
    is_cognito_identity_id,
    get_primary_user_id,
    should_support_legacy_id
)


class TestMigrationDetection:
    """Test migration detection logic"""
    
    def test_new_cognito_user_no_migration(self):
        """Test that new Cognito users don't trigger migration"""
        event_body = {
            'cognito_identity_id': 'us-east-1:12345678-1234-1234-1234-123456789012'
        }
        
        needs_migration, legacy_id, cognito_id = detect_migration_needed(event_body)
        
        assert needs_migration is False
        assert legacy_id is None
        assert cognito_id == 'us-east-1:12345678-1234-1234-1234-123456789012'
    
    def test_legacy_user_with_cognito_triggers_migration(self):
        """Test that legacy user with Cognito ID triggers migration"""
        event_body = {
            'user_id': 'farmer_abc123',
            'cognito_identity_id': 'us-east-1:12345678-1234-1234-1234-123456789012'
        }
        
        needs_migration, legacy_id, cognito_id = detect_migration_needed(event_body)
        
        assert needs_migration is True
        assert legacy_id == 'farmer_abc123'
        assert cognito_id == 'us-east-1:12345678-1234-1234-1234-123456789012'
    
    def test_legacy_user_without_cognito_no_migration(self):
        """Test that legacy user without Cognito ID doesn't trigger migration (backward compat)"""
        event_body = {
            'user_id': 'farmer_xyz789'
        }
        
        needs_migration, legacy_id, cognito_id = detect_migration_needed(event_body)
        
        assert needs_migration is False
        assert legacy_id == 'farmer_xyz789'
        assert cognito_id is None
    
    def test_already_migrated_user_no_migration(self):
        """Test that already migrated users don't trigger migration"""
        event_body = {
            'user_id': 'us-east-1:87654321-4321-4321-4321-210987654321'
        }
        
        needs_migration, legacy_id, cognito_id = detect_migration_needed(event_body)
        
        assert needs_migration is False
        assert legacy_id is None
        assert cognito_id == 'us-east-1:87654321-4321-4321-4321-210987654321'
    
    def test_unknown_format_no_migration(self):
        """Test that unknown user ID format doesn't trigger migration"""
        event_body = {
            'user_id': 'unknown_format_123'
        }
        
        needs_migration, legacy_id, cognito_id = detect_migration_needed(event_body)
        
        assert needs_migration is False
        assert legacy_id == 'unknown_format_123'
        assert cognito_id is None


class TestUserIdValidation:
    """Test user ID format validation functions"""
    
    def test_is_legacy_user_id_valid(self):
        """Test legacy user ID detection"""
        assert is_legacy_user_id('farmer_abc123') is True
        assert is_legacy_user_id('farmer_xyz') is True
        assert is_legacy_user_id('farmer_') is True
    
    def test_is_legacy_user_id_invalid(self):
        """Test non-legacy user ID detection"""
        assert is_legacy_user_id('us-east-1:12345678-1234-1234-1234-123456789012') is False
        assert is_legacy_user_id('user_abc123') is False
        assert is_legacy_user_id('') is False
        assert is_legacy_user_id(None) is False
    
    def test_is_cognito_identity_id_valid(self):
        """Test Cognito Identity ID detection"""
        assert is_cognito_identity_id('us-east-1:12345678-1234-1234-1234-123456789012') is True
        assert is_cognito_identity_id('eu-west-1:87654321-4321-4321-4321-210987654321') is True
    
    def test_is_cognito_identity_id_invalid(self):
        """Test non-Cognito ID detection"""
        assert is_cognito_identity_id('farmer_abc123') is False
        assert is_cognito_identity_id('invalid:format:extra') is False
        assert is_cognito_identity_id('no_colon') is False
        assert is_cognito_identity_id('') is False
        assert is_cognito_identity_id(None) is False


class TestPrimaryUserId:
    """Test primary user ID selection logic"""
    
    def test_get_primary_user_id_prefers_cognito(self):
        """Test that Cognito ID is preferred over legacy ID"""
        event_body = {
            'user_id': 'farmer_abc123',
            'cognito_identity_id': 'us-east-1:12345678-1234-1234-1234-123456789012'
        }
        
        primary_id = get_primary_user_id(event_body)
        
        assert primary_id == 'us-east-1:12345678-1234-1234-1234-123456789012'
    
    def test_get_primary_user_id_falls_back_to_user_id(self):
        """Test fallback to user_id when Cognito ID not present"""
        event_body = {
            'user_id': 'farmer_xyz789'
        }
        
        primary_id = get_primary_user_id(event_body)
        
        assert primary_id == 'farmer_xyz789'
    
    def test_get_primary_user_id_raises_on_missing_ids(self):
        """Test that missing IDs raise ValueError"""
        event_body = {}
        
        with pytest.raises(ValueError, match="Missing user_id or cognito_identity_id"):
            get_primary_user_id(event_body)


class TestLegacySupport:
    """Test legacy user ID support logic"""
    
    def test_should_support_legacy_id_for_farmer_prefix(self):
        """Test that legacy IDs are supported during migration window"""
        assert should_support_legacy_id('farmer_abc123') is True
        assert should_support_legacy_id('farmer_xyz') is True
    
    def test_should_not_support_non_legacy_id(self):
        """Test that non-legacy IDs are not supported"""
        assert should_support_legacy_id('us-east-1:12345678-1234-1234-1234-123456789012') is False
        assert should_support_legacy_id('user_abc123') is False



class TestMigrateUserData:
    """Test user data migration function"""
    
    @patch('src.utils.migration_handler.dynamodb')
    @patch('src.utils.ttl_manager.TTLManager')
    def test_migrate_user_data_success(self, mock_ttl_manager, mock_dynamodb):
        """Test successful migration of user data"""
        from src.utils.migration_handler import migrate_user_data
        
        # Mock TTL manager
        mock_ttl_instance = Mock()
        mock_ttl_instance.calculate_expiry_time.return_value = 1234567890
        mock_ttl_manager.return_value = mock_ttl_instance
        
        # Mock DynamoDB tables
        mock_migrations_table = Mock()
        mock_conversations_table = Mock()
        mock_user_table = Mock()
        
        mock_dynamodb.Table.side_effect = lambda name: {
            'ure-user-migrations': mock_migrations_table,
            'ure-conversations': mock_conversations_table,
            'ure-user-profiles': mock_user_table
        }[name]
        
        # Mock migration check (not already migrated)
        mock_migrations_table.get_item.return_value = {}
        
        # Mock conversations data
        mock_conversations_table.get_item.return_value = {
            'Item': {
                'user_id': 'farmer_abc123',
                'conversations': [
                    {'query': 'test1', 'response': 'answer1'},
                    {'query': 'test2', 'response': 'answer2'}
                ]
            }
        }
        
        # Mock profile data
        mock_user_table.get_item.return_value = {
            'Item': {
                'user_id': 'farmer_abc123',
                'location': 'Maharashtra',
                'language': 'mr'
            }
        }
        
        # Execute migration
        result = migrate_user_data(
            'farmer_abc123',
            'us-east-1:12345678-1234-1234-1234-123456789012'
        )
        
        # Verify result
        assert result['success'] is True
        assert result['already_migrated'] is False
        assert result['conversations_migrated'] == 2
        assert result['profile_migrated'] is True
        
        # Verify conversations were copied
        assert mock_conversations_table.put_item.called
        
        # Verify profile was copied
        assert mock_user_table.put_item.called
        
        # Verify TTL was set on legacy records
        assert mock_conversations_table.update_item.called
        assert mock_user_table.update_item.called
        
        # Verify migration was recorded
        assert mock_migrations_table.put_item.called
    
    @patch('src.utils.migration_handler.dynamodb')
    def test_migrate_user_data_already_migrated(self, mock_dynamodb):
        """Test idempotency - migration already completed"""
        from src.utils.migration_handler import migrate_user_data
        
        # Mock migrations table
        mock_migrations_table = Mock()
        mock_dynamodb.Table.return_value = mock_migrations_table
        
        # Mock existing migration
        mock_migrations_table.get_item.return_value = {
            'Item': {
                'legacy_user_id': 'farmer_abc123',
                'cognito_identity_id': 'us-east-1:12345678-1234-1234-1234-123456789012',
                'migration_date': '2026-03-04T10:00:00'
            }
        }
        
        # Execute migration
        result = migrate_user_data(
            'farmer_abc123',
            'us-east-1:12345678-1234-1234-1234-123456789012'
        )
        
        # Verify idempotency
        assert result['success'] is True
        assert result['already_migrated'] is True
        assert 'migration_date' in result
    
    @patch('src.utils.migration_handler.dynamodb')
    @patch('src.utils.ttl_manager.TTLManager')
    def test_migrate_empty_user_data(self, mock_ttl_manager, mock_dynamodb):
        """Test migration for user with no existing data"""
        from src.utils.migration_handler import migrate_user_data
        
        # Mock TTL manager
        mock_ttl_instance = Mock()
        mock_ttl_instance.calculate_expiry_time.return_value = 1234567890
        mock_ttl_manager.return_value = mock_ttl_instance
        
        # Mock DynamoDB tables
        mock_migrations_table = Mock()
        mock_conversations_table = Mock()
        mock_user_table = Mock()
        
        mock_dynamodb.Table.side_effect = lambda name: {
            'ure-user-migrations': mock_migrations_table,
            'ure-conversations': mock_conversations_table,
            'ure-user-profiles': mock_user_table
        }[name]
        
        # Mock migration check (not already migrated)
        mock_migrations_table.get_item.return_value = {}
        
        # Mock empty conversations and profile
        mock_conversations_table.get_item.return_value = {}
        mock_user_table.get_item.return_value = {}
        
        # Execute migration
        result = migrate_user_data(
            'farmer_new123',
            'us-east-1:99999999-9999-9999-9999-999999999999'
        )
        
        # Verify result
        assert result['success'] is True
        assert result['conversations_migrated'] == 0
        assert result['profile_migrated'] is False
        
        # Verify migration was still recorded
        assert mock_migrations_table.put_item.called
    
    @patch('src.utils.migration_handler.dynamodb')
    def test_migrate_user_data_conversations_error(self, mock_dynamodb):
        """Test migration failure when conversations copy fails"""
        from src.utils.migration_handler import migrate_user_data
        
        # Mock DynamoDB tables
        mock_migrations_table = Mock()
        mock_conversations_table = Mock()
        
        mock_dynamodb.Table.side_effect = lambda name: {
            'ure-user-migrations': mock_migrations_table,
            'ure-conversations': mock_conversations_table
        }[name]
        
        # Mock migration check (not already migrated)
        mock_migrations_table.get_item.return_value = {}
        
        # Mock conversations error
        mock_conversations_table.get_item.side_effect = ClientError(
            {'Error': {'Code': 'InternalServerError', 'Message': 'DynamoDB error'}},
            'GetItem'
        )
        
        # Execute migration
        result = migrate_user_data(
            'farmer_error123',
            'us-east-1:88888888-8888-8888-8888-888888888888'
        )
        
        # Verify error handling
        assert result['success'] is False
        assert 'error' in result
        assert 'Failed to migrate conversations' in result['error']
