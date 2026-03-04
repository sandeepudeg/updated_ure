#!/usr/bin/env python3
"""
Migration Handler - Legacy User Migration Component
Handles seamless migration from localStorage-based user IDs to Cognito Identity IDs
"""

import logging
from typing import Dict, Any, Tuple, Optional
import boto3
from botocore.exceptions import ClientError
import os
from datetime import datetime

logger = logging.getLogger(__name__)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')

# Environment variables
CONVERSATIONS_TABLE = os.environ.get('DYNAMODB_TABLE_NAME', 'ure-conversations')
USER_TABLE = os.environ.get('DYNAMODB_USER_TABLE', 'ure-user-profiles')
MIGRATIONS_TABLE = os.environ.get('MIGRATIONS_TABLE', 'ure-user-migrations')


def detect_migration_needed(event_body: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Detect if user needs migration based on request parameters
    
    Args:
        event_body: Request body containing user_id and/or cognito_identity_id
    
    Returns:
        tuple: (needs_migration, legacy_user_id, cognito_identity_id)
            - needs_migration: True if migration should be performed
            - legacy_user_id: Legacy user ID (farmer_*) or None
            - cognito_identity_id: Cognito Identity ID or None
    """
    user_id = event_body.get('user_id')
    cognito_identity_id = event_body.get('cognito_identity_id')
    
    # Case 1: New user with Cognito ID only
    if cognito_identity_id and not user_id:
        logger.debug(f"New Cognito user detected: {cognito_identity_id[:20]}...")
        return False, None, cognito_identity_id
    
    # Case 2: Legacy user with old ID format (farmer_*)
    if user_id and user_id.startswith('farmer_'):
        # Check if Cognito ID also provided (migration in progress)
        if cognito_identity_id:
            logger.info(f"Migration needed: {user_id} -> {cognito_identity_id[:20]}...")
            return True, user_id, cognito_identity_id
        else:
            # Legacy user without Cognito ID yet (backward compatibility)
            logger.debug(f"Legacy user without Cognito ID: {user_id}")
            return False, user_id, None
    
    # Case 3: Already migrated (Cognito ID format: region:uuid)
    if user_id and ':' in user_id:
        logger.debug(f"Already migrated user: {user_id[:20]}...")
        return False, None, user_id
    
    # Case 4: Unknown format
    logger.warning(f"Unknown user ID format: {user_id}")
    return False, user_id, cognito_identity_id


def is_legacy_user_id(user_id: str) -> bool:
    """
    Check if a user ID is in legacy format
    
    Args:
        user_id: User identifier
    
    Returns:
        bool: True if legacy format (farmer_*)
    """
    if not user_id:
        return False
    
    return user_id.startswith('farmer_')


def is_cognito_identity_id(user_id: str) -> bool:
    """
    Check if a user ID is a Cognito Identity ID
    
    Args:
        user_id: User identifier
    
    Returns:
        bool: True if Cognito format (region:uuid)
    """
    if not user_id:
        return False
    
    # Cognito Identity IDs have format: region:uuid
    # Example: us-east-1:12345678-1234-1234-1234-123456789012
    return ':' in user_id and user_id.count(':') == 1


def get_primary_user_id(event_body: Dict[str, Any]) -> str:
    """
    Get the primary user ID to use for this request
    
    Priority:
    1. Cognito Identity ID (if present)
    2. User ID (legacy or Cognito format)
    
    Args:
        event_body: Request body
    
    Returns:
        str: Primary user ID to use
    """
    cognito_identity_id = event_body.get('cognito_identity_id')
    user_id = event_body.get('user_id')
    
    # Prefer Cognito ID if available
    if cognito_identity_id:
        return cognito_identity_id
    
    # Fall back to user_id
    if user_id:
        return user_id
    
    # No user ID provided
    logger.error("No user ID provided in request")
    raise ValueError("Missing user_id or cognito_identity_id")


def should_support_legacy_id(user_id: str) -> bool:
    """
    Check if legacy user ID should still be supported (30-day window)
    
    For MVP, we support legacy IDs for 30 days after deployment.
    This function can be enhanced to check deployment date.
    
    Args:
        user_id: User identifier
    
    Returns:
        bool: True if legacy ID should be supported
    """
    # For MVP, always support legacy IDs during migration window
    # Post-MVP: Check against deployment date
    return is_legacy_user_id(user_id)



def migrate_user_data(legacy_user_id: str, cognito_identity_id: str) -> Dict[str, Any]:
    """
    Migrate user data from legacy user ID to Cognito Identity ID
    
    This function:
    1. Checks if migration already completed (idempotency)
    2. Copies conversations from legacy ID to Cognito ID
    3. Copies user profile from legacy ID to Cognito ID
    4. Sets short TTL (1 hour) on legacy records for cleanup
    5. Records migration in tracking table with 30-day TTL
    
    Args:
        legacy_user_id: Legacy user ID (farmer_*)
        cognito_identity_id: Cognito Identity ID (region:uuid)
    
    Returns:
        dict: Migration result with status and details
            {
                'success': bool,
                'already_migrated': bool,
                'conversations_migrated': int,
                'profile_migrated': bool,
                'error': str (if failed)
            }
    """
    try:
        # Step 1: Check if migration already completed (idempotency)
        migrations_table = dynamodb.Table(MIGRATIONS_TABLE)
        
        try:
            existing_migration = migrations_table.get_item(
                Key={'legacy_user_id': legacy_user_id}
            )
            
            if 'Item' in existing_migration:
                logger.info(f"Migration already completed for {legacy_user_id}")
                return {
                    'success': True,
                    'already_migrated': True,
                    'cognito_identity_id': existing_migration['Item']['cognito_identity_id'],
                    'migration_date': existing_migration['Item']['migration_date']
                }
        except ClientError as e:
            logger.error(f"Failed to check migration status: {e}")
            # Continue with migration if check fails
        
        # Step 2: Copy conversations from legacy ID to Cognito ID
        conversations_table = dynamodb.Table(CONVERSATIONS_TABLE)
        conversations_migrated = 0
        
        try:
            # Get legacy conversations
            legacy_conversations = conversations_table.get_item(
                Key={'user_id': legacy_user_id}
            )
            
            if 'Item' in legacy_conversations:
                conversations_data = legacy_conversations['Item'].get('conversations', [])
                conversations_migrated = len(conversations_data)
                
                # Copy to Cognito ID
                conversations_table.put_item(Item={
                    'user_id': cognito_identity_id,
                    'conversations': conversations_data,
                    'last_updated': datetime.utcnow().isoformat(),
                    'migrated_from': legacy_user_id,
                    'migration_date': datetime.utcnow().isoformat()
                })
                
                logger.info(f"Migrated {conversations_migrated} conversations from {legacy_user_id} to {cognito_identity_id}")
                
                # Set short TTL (1 hour = 3600 seconds) on legacy record
                from .ttl_manager import TTLManager
                ttl_manager = TTLManager()
                legacy_expiry = ttl_manager.calculate_expiry_time(duration_seconds=3600)
                
                conversations_table.update_item(
                    Key={'user_id': legacy_user_id},
                    UpdateExpression='SET expiry_time = :expiry',
                    ExpressionAttributeValues={':expiry': legacy_expiry}
                )
                
                logger.info(f"Set 1-hour TTL on legacy conversations for {legacy_user_id}")
            else:
                logger.info(f"No conversations found for legacy user {legacy_user_id}")
        
        except ClientError as e:
            logger.error(f"Failed to migrate conversations: {e}")
            return {
                'success': False,
                'error': f"Failed to migrate conversations: {str(e)}"
            }
        
        # Step 3: Copy user profile from legacy ID to Cognito ID
        user_table = dynamodb.Table(USER_TABLE)
        profile_migrated = False
        
        try:
            # Get legacy profile
            legacy_profile = user_table.get_item(
                Key={'user_id': legacy_user_id}
            )
            
            if 'Item' in legacy_profile:
                profile_data = legacy_profile['Item']
                
                # Update user_id to Cognito ID
                profile_data['user_id'] = cognito_identity_id
                profile_data['migrated_from'] = legacy_user_id
                profile_data['migration_date'] = datetime.utcnow().isoformat()
                profile_data['last_updated'] = datetime.utcnow().isoformat()
                
                # Copy to Cognito ID
                user_table.put_item(Item=profile_data)
                profile_migrated = True
                
                logger.info(f"Migrated profile from {legacy_user_id} to {cognito_identity_id}")
                
                # Set short TTL (1 hour) on legacy profile
                from .ttl_manager import TTLManager
                ttl_manager = TTLManager()
                legacy_expiry = ttl_manager.calculate_expiry_time(duration_seconds=3600)
                
                user_table.update_item(
                    Key={'user_id': legacy_user_id},
                    UpdateExpression='SET expiry_time = :expiry',
                    ExpressionAttributeValues={':expiry': legacy_expiry}
                )
                
                logger.info(f"Set 1-hour TTL on legacy profile for {legacy_user_id}")
            else:
                logger.info(f"No profile found for legacy user {legacy_user_id}")
        
        except ClientError as e:
            logger.error(f"Failed to migrate profile: {e}")
            # Don't fail entire migration if profile migration fails
            # Conversations are more critical
        
        # Step 4: Record migration in tracking table with 30-day TTL
        try:
            from .ttl_manager import TTLManager
            ttl_manager = TTLManager()
            # 30 days = 30 * 24 * 60 * 60 = 2592000 seconds
            migration_expiry = ttl_manager.calculate_expiry_time(duration_seconds=2592000)
            
            migrations_table.put_item(Item={
                'legacy_user_id': legacy_user_id,
                'cognito_identity_id': cognito_identity_id,
                'migration_date': datetime.utcnow().isoformat(),
                'conversations_migrated': conversations_migrated,
                'profile_migrated': profile_migrated,
                'expiry_time': migration_expiry
            })
            
            # Also create reverse lookup entry (GSI)
            migrations_table.put_item(Item={
                'legacy_user_id': f"cognito#{cognito_identity_id}",
                'cognito_identity_id': legacy_user_id,
                'migration_date': datetime.utcnow().isoformat(),
                'is_reverse_lookup': True,
                'expiry_time': migration_expiry
            })
            
            logger.info(f"Recorded migration in tracking table: {legacy_user_id} -> {cognito_identity_id}")
        
        except ClientError as e:
            logger.error(f"Failed to record migration: {e}")
            # Don't fail entire migration if tracking fails
        
        return {
            'success': True,
            'already_migrated': False,
            'conversations_migrated': conversations_migrated,
            'profile_migrated': profile_migrated,
            'legacy_user_id': legacy_user_id,
            'cognito_identity_id': cognito_identity_id,
            'migration_date': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Unexpected error during migration: {e}", exc_info=True)
        return {
            'success': False,
            'error': f"Unexpected error: {str(e)}"
        }
