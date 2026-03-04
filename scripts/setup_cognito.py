#!/usr/bin/env python3
"""
Create Cognito Identity Pool and IAM roles for GramSetu MVP
Implements anonymous authentication for privacy-preserving user access
"""

import boto3
import json
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# AWS Configuration
REGION = 'us-east-1'
ACCOUNT_ID = '188238313375'

def create_cognito_identity_pool():
    """Create Cognito Identity Pool for anonymous users"""
    cognito = boto3.client('cognito-identity', region_name=REGION)
    
    try:
        response = cognito.create_identity_pool(
            IdentityPoolName='GramSetuAnonymousUsers',
            AllowUnauthenticatedIdentities=True,
            AllowClassicFlow=False
        )
        
        identity_pool_id = response['IdentityPoolId']
        logger.info(f"✓ Created Cognito Identity Pool: {identity_pool_id}")
        return identity_pool_id
    
    except cognito.exceptions.ResourceConflictException:
        # Pool already exists - find it
        logger.info("Cognito Identity Pool already exists, finding existing pool...")
        pools = cognito.list_identity_pools(MaxResults=60)
        for pool in pools['IdentityPools']:
            if pool['IdentityPoolName'] == 'GramSetuAnonymousUsers':
                logger.info(f"✓ Found existing Cognito Identity Pool: {pool['IdentityPoolId']}")
                return pool['IdentityPoolId']
        
        logger.error("Pool exists but couldn't be found in list")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"✗ Failed to create Cognito Identity Pool: {e}")
        sys.exit(1)


def create_unauthenticated_role(identity_pool_id):
    """Create IAM role for unauthenticated Cognito users"""
    iam = boto3.client('iam', region_name=REGION)
    
    # Trust policy for Cognito
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Federated": "cognito-identity.amazonaws.com"
                },
                "Action": "sts:AssumeRoleWithWebIdentity",
                "Condition": {
                    "StringEquals": {
                        "cognito-identity.amazonaws.com:aud": identity_pool_id
                    },
                    "ForAnyValue:StringLike": {
                        "cognito-identity.amazonaws.com:amr": "unauthenticated"
                    }
                }
            }
        ]
    }
    
    # Permissions policy
    permissions_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "execute-api:Invoke"
                ],
                "Resource": f"arn:aws:execute-api:{REGION}:*:*/*/POST/*"
            }
        ]
    }
    
    role_name = 'GramSetuCognitoUnauthenticatedRole'
    
    try:
        # Create role
        role_response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for unauthenticated Cognito users in GramSetu'
        )
        
        role_arn = role_response['Role']['Arn']
        logger.info(f"✓ Created IAM role: {role_arn}")
        
        # Attach inline policy
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName='GramSetuAPIAccess',
            PolicyDocument=json.dumps(permissions_policy)
        )
        
        logger.info(f"✓ Attached permissions policy to role")
        return role_arn
    
    except iam.exceptions.EntityAlreadyExistsException:
        role = iam.get_role(RoleName=role_name)
        logger.info(f"✓ IAM role already exists: {role['Role']['Arn']}")
        return role['Role']['Arn']
    
    except Exception as e:
        logger.error(f"✗ Failed to create IAM role: {e}")
        sys.exit(1)


def attach_role_to_identity_pool(identity_pool_id, role_arn):
    """Attach IAM role to Cognito Identity Pool"""
    cognito = boto3.client('cognito-identity', region_name=REGION)
    
    try:
        cognito.set_identity_pool_roles(
            IdentityPoolId=identity_pool_id,
            Roles={
                'unauthenticated': role_arn
            }
        )
        logger.info(f"✓ Attached role to Identity Pool")
    
    except Exception as e:
        logger.error(f"✗ Failed to attach role: {e}")
        sys.exit(1)


def create_migration_table():
    """Create DynamoDB table for tracking migrations"""
    dynamodb = boto3.client('dynamodb', region_name=REGION)
    
    try:
        response = dynamodb.create_table(
            TableName='ure-user-migrations',
            KeySchema=[
                {'AttributeName': 'legacy_user_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'legacy_user_id', 'AttributeType': 'S'},
                {'AttributeName': 'cognito_identity_id', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'cognito_identity_id-index',
                    'KeySchema': [
                        {'AttributeName': 'cognito_identity_id', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            SSESpecification={
                'Enabled': True,
                'SSEType': 'KMS'
            }
        )
        
        logger.info(f"✓ Created migration table: ure-user-migrations")
        
        # Wait for table to be active
        logger.info("Waiting for table to become active...")
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName='ure-user-migrations')
        logger.info(f"✓ Migration table is active")
    
    except dynamodb.exceptions.ResourceInUseException:
        logger.info(f"✓ Migration table already exists")
    
    except Exception as e:
        logger.error(f"✗ Failed to create migration table: {e}")
        sys.exit(1)


def main():
    """Setup Cognito and related infrastructure"""
    logger.info("=" * 60)
    logger.info("GramSetu Privacy MVP - Cognito Setup")
    logger.info("=" * 60)
    logger.info("")
    
    # Create Cognito Identity Pool
    logger.info("Step 1: Creating Cognito Identity Pool...")
    identity_pool_id = create_cognito_identity_pool()
    logger.info("")
    
    # Create IAM role
    logger.info("Step 2: Creating IAM role for unauthenticated users...")
    role_arn = create_unauthenticated_role(identity_pool_id)
    logger.info("")
    
    # Attach role to pool
    logger.info("Step 3: Attaching role to Identity Pool...")
    attach_role_to_identity_pool(identity_pool_id, role_arn)
    logger.info("")
    
    # Create migration table
    logger.info("Step 4: Creating user migration tracking table...")
    create_migration_table()
    logger.info("")
    
    logger.info("=" * 60)
    logger.info("✓ Infrastructure setup complete!")
    logger.info("=" * 60)
    logger.info("")
    logger.info(f"Cognito Identity Pool ID: {identity_pool_id}")
    logger.info(f"IAM Role ARN: {role_arn}")
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Add this to your frontend configuration:")
    logger.info(f"   COGNITO_IDENTITY_POOL_ID='{identity_pool_id}'")
    logger.info("")
    logger.info("2. Save the Identity Pool ID for Lambda deployment")
    logger.info("")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
