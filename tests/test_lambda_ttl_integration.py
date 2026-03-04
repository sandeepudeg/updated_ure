#!/usr/bin/env python3
"""
Unit tests for Lambda handler TTL integration
Tests that TTL is calculated and extended correctly on conversation storage
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time


class TestLambdaTTLIntegration:
    """Test TTL integration in Lambda handler"""
    
    @patch('src.aws.lambda_handler.dynamodb')
    def test_store_conversation_with_new_ttl(
        self,
        mock_dynamodb
    ):
        """Test that new conversations get TTL set"""
        from src.aws.lambda_handler import store_conversation
        
        # Mock DynamoDB table (no existing conversations)
        mock_table = Mock()
        mock_table.get_item.return_value = {}
        mock_dynamodb.Table.return_value = mock_table
        
        # Store conversation
        current_time = int(time.time())
        store_conversation(
            user_id='test_user',
            query='test query',
            response='test response',
            agent_used='test_agent'
        )
        
        # Verify conversation was stored with TTL
        assert mock_table.put_item.called
        stored_item = mock_table.put_item.call_args[1]['Item']
        assert 'expiry_time' in stored_item
        assert stored_item['user_id'] == 'test_user'
        
        # Verify TTL is approximately 3 hours in the future (10800 seconds ±60 seconds)
        expiry_time = stored_item['expiry_time']
        expected_expiry = current_time + 10800
        assert abs(expiry_time - expected_expiry) < 60, \
            f"TTL {expiry_time} is not within 60 seconds of expected {expected_expiry}"
    
    @patch('src.aws.lambda_handler.dynamodb')
    def test_store_conversation_extends_existing_ttl(
        self,
        mock_dynamodb
    ):
        """Test that existing sessions get TTL extended"""
        from src.aws.lambda_handler import store_conversation
        
        # Mock DynamoDB table (existing conversation with TTL)
        old_expiry = int(time.time()) + 5000  # Expires in ~1.4 hours
        mock_table = Mock()
        mock_table.get_item.return_value = {
            'Item': {
                'conversations': [
                    {'query': 'old query', 'response': 'old response'}
                ],
                'expiry_time': old_expiry
            }
        }
        mock_dynamodb.Table.return_value = mock_table
        
        # Store new conversation
        current_time = int(time.time())
        store_conversation(
            user_id='test_user',
            query='new query',
            response='new response',
            agent_used='test_agent'
        )
        
        # Verify conversation was stored with extended TTL
        assert mock_table.put_item.called
        stored_item = mock_table.put_item.call_args[1]['Item']
        assert 'expiry_time' in stored_item
        assert len(stored_item['conversations']) == 2
        
        # Verify TTL was extended (should be ~3 hours from now, not from old expiry)
        new_expiry = stored_item['expiry_time']
        expected_expiry = current_time + 10800
        assert abs(new_expiry - expected_expiry) < 60, \
            f"Extended TTL {new_expiry} is not within 60 seconds of expected {expected_expiry}"
        assert new_expiry > old_expiry, "TTL should be extended, not kept the same"
    
    @patch('src.aws.lambda_handler.dynamodb')
    def test_ttl_with_ip_hashing_combined(
        self,
        mock_dynamodb
    ):
        """Test that TTL and IP hashing work together"""
        from src.aws.lambda_handler import store_conversation
        
        # Mock DynamoDB table
        mock_table = Mock()
        mock_table.get_item.return_value = {}
        mock_dynamodb.Table.return_value = mock_table
        
        # Mock IP hasher
        with patch('src.aws.lambda_handler.get_ip_hasher') as mock_get_ip_hasher:
            mock_hasher = Mock()
            mock_hasher.extract_and_hash_ip.return_value = 'a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456'
            mock_get_ip_hasher.return_value = mock_hasher
            
            # Create event with IP
            event = {
                'requestContext': {
                    'identity': {
                        'sourceIp': '192.168.1.1'
                    }
                }
            }
            
            # Store conversation with both TTL and IP hashing
            current_time = int(time.time())
            store_conversation(
                user_id='test_user',
                query='test query',
                response='test response',
                agent_used='test_agent',
                event=event
            )
            
            # Verify both TTL and hashed IP are present
            stored_item = mock_table.put_item.call_args[1]['Item']
            assert 'expiry_time' in stored_item
            assert stored_item['conversations'][0]['metadata']['hashed_ip'] == 'a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456'
            
            # Verify TTL is correct
            expiry_time = stored_item['expiry_time']
            expected_expiry = current_time + 10800
            assert abs(expiry_time - expected_expiry) < 60
    
    @patch('src.aws.lambda_handler.dynamodb')
    def test_ttl_extends_on_multiple_interactions(
        self,
        mock_dynamodb
    ):
        """Test that TTL is extended on every user interaction"""
        from src.aws.lambda_handler import store_conversation
        
        # Mock DynamoDB table
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        
        # First interaction - no existing TTL
        mock_table.get_item.return_value = {}
        time_1 = int(time.time())
        store_conversation(
            user_id='test_user',
            query='query 1',
            response='response 1',
            agent_used='test_agent'
        )
        
        # Verify initial TTL was set
        stored_item_1 = mock_table.put_item.call_args[1]['Item']
        expiry_1 = stored_item_1['expiry_time']
        assert abs(expiry_1 - (time_1 + 10800)) < 60
        
        # Second interaction after 2 seconds - TTL should be extended
        time.sleep(2)  # Wait 2 seconds to ensure time difference
        mock_table.get_item.return_value = {
            'Item': {
                'conversations': [{'query': 'query 1'}],
                'expiry_time': expiry_1
            }
        }
        time_2 = int(time.time())
        store_conversation(
            user_id='test_user',
            query='query 2',
            response='response 2',
            agent_used='test_agent'
        )
        
        # Verify TTL was extended
        stored_item_2 = mock_table.put_item.call_args[1]['Item']
        expiry_2 = stored_item_2['expiry_time']
        assert expiry_2 >= expiry_1, "TTL should be extended or stay the same on second interaction"
        assert abs(expiry_2 - (time_2 + 10800)) < 60
