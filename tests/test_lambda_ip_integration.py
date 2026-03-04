#!/usr/bin/env python3
"""
Unit tests for Lambda handler IP hashing integration
Tests that IP addresses are hashed and stored correctly
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json


class TestLambdaIPIntegration:
    """Test IP hashing integration in Lambda handler"""
    
    @patch('src.aws.lambda_handler.dynamodb')
    @patch('src.aws.lambda_handler.get_ip_hasher')
    @patch('src.aws.lambda_handler.invoke_supervisor_agent')
    @patch('src.aws.lambda_handler.get_user_context')
    def test_store_conversation_with_hashed_ip(
        self,
        mock_get_user_context,
        mock_invoke_supervisor,
        mock_get_ip_hasher,
        mock_dynamodb
    ):
        """Test that conversations are stored with hashed IP"""
        from src.aws.lambda_handler import store_conversation
        
        # Mock IP hasher
        mock_hasher = Mock()
        mock_hasher.extract_and_hash_ip.return_value = 'hashed_192.168.1.1'
        mock_get_ip_hasher.return_value = mock_hasher
        
        # Mock DynamoDB table
        mock_table = Mock()
        mock_table.get_item.return_value = {'Item': {'conversations': []}}
        mock_dynamodb.Table.return_value = mock_table
        
        # Create test event with IP address
        event = {
            'requestContext': {
                'identity': {
                    'sourceIp': '192.168.1.1'
                }
            }
        }
        
        # Store conversation
        store_conversation(
            user_id='test_user',
            query='test query',
            response='test response',
            agent_used='test_agent',
            metadata={'test': 'data'},
            event=event
        )
        
        # Verify IP hasher was called
        mock_hasher.extract_and_hash_ip.assert_called_once_with(event)
        
        # Verify conversation was stored with hashed IP
        assert mock_table.put_item.called
        stored_item = mock_table.put_item.call_args[1]['Item']
        assert stored_item['user_id'] == 'test_user'
        assert len(stored_item['conversations']) == 1
        
        conversation = stored_item['conversations'][0]
        assert conversation['query'] == 'test query'
        assert conversation['response'] == 'test response'
        assert conversation['metadata']['hashed_ip'] == 'hashed_192.168.1.1'
        assert conversation['metadata']['test'] == 'data'
    
    @patch('src.aws.lambda_handler.dynamodb')
    @patch('src.aws.lambda_handler.get_ip_hasher')
    def test_store_conversation_without_event(
        self,
        mock_get_ip_hasher,
        mock_dynamodb
    ):
        """Test that conversations can be stored without event (no IP hashing)"""
        from src.aws.lambda_handler import store_conversation
        
        # Mock DynamoDB table
        mock_table = Mock()
        mock_table.get_item.return_value = {'Item': {'conversations': []}}
        mock_dynamodb.Table.return_value = mock_table
        
        # Store conversation without event
        store_conversation(
            user_id='test_user',
            query='test query',
            response='test response',
            agent_used='test_agent',
            metadata={'test': 'data'}
        )
        
        # Verify IP hasher was NOT called
        mock_get_ip_hasher.assert_not_called()
        
        # Verify conversation was stored without hashed IP
        assert mock_table.put_item.called
        stored_item = mock_table.put_item.call_args[1]['Item']
        conversation = stored_item['conversations'][0]
        assert 'hashed_ip' not in conversation['metadata']
        assert conversation['metadata']['test'] == 'data'
    
    @patch('src.aws.lambda_handler.dynamodb')
    @patch('src.aws.lambda_handler.get_ip_hasher')
    def test_store_conversation_ip_hasher_unavailable(
        self,
        mock_get_ip_hasher,
        mock_dynamodb
    ):
        """Test graceful handling when IP hasher is unavailable"""
        from src.aws.lambda_handler import store_conversation
        
        # Mock IP hasher as unavailable
        mock_get_ip_hasher.return_value = None
        
        # Mock DynamoDB table
        mock_table = Mock()
        mock_table.get_item.return_value = {'Item': {'conversations': []}}
        mock_dynamodb.Table.return_value = mock_table
        
        # Create test event
        event = {
            'requestContext': {
                'identity': {
                    'sourceIp': '192.168.1.1'
                }
            }
        }
        
        # Store conversation - should not fail
        store_conversation(
            user_id='test_user',
            query='test query',
            response='test response',
            agent_used='test_agent',
            event=event
        )
        
        # Verify conversation was stored without hashed IP
        assert mock_table.put_item.called
        stored_item = mock_table.put_item.call_args[1]['Item']
        conversation = stored_item['conversations'][0]
        assert 'hashed_ip' not in conversation['metadata']
    
    @patch('src.aws.lambda_handler.dynamodb')
    @patch('src.aws.lambda_handler.get_ip_hasher')
    def test_no_plaintext_ip_in_stored_data(
        self,
        mock_get_ip_hasher,
        mock_dynamodb
    ):
        """Test that plaintext IP is NEVER stored in DynamoDB"""
        from src.aws.lambda_handler import store_conversation
        
        # Mock IP hasher with realistic hash (SHA-256 hex)
        mock_hasher = Mock()
        mock_hasher.extract_and_hash_ip.return_value = 'a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456'
        mock_get_ip_hasher.return_value = mock_hasher
        
        # Mock DynamoDB table
        mock_table = Mock()
        mock_table.get_item.return_value = {'Item': {'conversations': []}}
        mock_dynamodb.Table.return_value = mock_table
        
        # Create test event with plaintext IP
        plaintext_ip = '10.0.0.1'
        event = {
            'requestContext': {
                'identity': {
                    'sourceIp': plaintext_ip
                }
            }
        }
        
        # Store conversation
        store_conversation(
            user_id='test_user',
            query='test query',
            response='test response',
            agent_used='test_agent',
            event=event
        )
        
        # Verify stored data
        stored_item = mock_table.put_item.call_args[1]['Item']
        stored_json = json.dumps(stored_item)
        
        # CRITICAL: Plaintext IP must NOT appear anywhere in stored data
        assert plaintext_ip not in stored_json, "Plaintext IP found in stored data!"
        
        # Verify only hashed IP is present
        assert 'a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456' in stored_json
