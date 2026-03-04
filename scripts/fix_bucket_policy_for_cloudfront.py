#!/usr/bin/env python3
"""
Fix S3 Bucket Policy to Allow CloudFront OAI Access
"""

import boto3
import json

BUCKET_NAME = "ure-mvp-data-us-east-1-188238313375"
OAI_CANONICAL_USER_ID = "e98c2c7ed09265a1355cd48381b028e12cb5a18fc1cc4cb4cc0ca957cc22bf7e4d51289d0cd89d86cd3dc2e8c471d09f"

def fix_bucket_policy():
    """Add CloudFront OAI to bucket policy"""
    s3_client = boto3.client('s3')
    
    print("=" * 60)
    print("Fixing S3 Bucket Policy for CloudFront Access")
    print("=" * 60)
    
    try:
        # Get current policy
        print(f"\n1. Getting current bucket policy...")
        response = s3_client.get_bucket_policy(Bucket=BUCKET_NAME)
        policy = json.loads(response['Policy'])
        print(f"✓ Current policy retrieved")
        print(f"  Statements: {len(policy['Statement'])}")
        
        # Check if CloudFront OAI statement already exists
        cloudfront_statement_exists = False
        for statement in policy['Statement']:
            if statement.get('Sid') == 'CloudFrontOAIAccessWebUI':
                cloudfront_statement_exists = True
                print(f"✓ CloudFront OAI statement already exists")
                break
        
        if not cloudfront_statement_exists:
            # Add CloudFront OAI statement
            print(f"\n2. Adding CloudFront OAI statement...")
            
            cloudfront_statement = {
                'Sid': 'CloudFrontOAIAccessWebUI',
                'Effect': 'Allow',
                'Principal': {
                    'CanonicalUser': OAI_CANONICAL_USER_ID
                },
                'Action': 's3:GetObject',
                'Resource': f'arn:aws:s3:::{BUCKET_NAME}/web-ui/*'
            }
            
            policy['Statement'].append(cloudfront_statement)
            
            # Update bucket policy
            print(f"3. Updating bucket policy...")
            s3_client.put_bucket_policy(
                Bucket=BUCKET_NAME,
                Policy=json.dumps(policy)
            )
            
            print(f"✓ Bucket policy updated successfully")
        
        # Verify policy
        print(f"\n4. Verifying updated policy...")
        response = s3_client.get_bucket_policy(Bucket=BUCKET_NAME)
        updated_policy = json.loads(response['Policy'])
        
        print(f"✓ Policy verified")
        print(f"  Total statements: {len(updated_policy['Statement'])}")
        
        for i, statement in enumerate(updated_policy['Statement'], 1):
            print(f"  Statement {i}: {statement.get('Sid', 'No Sid')}")
        
        print("\n" + "=" * 60)
        print("Bucket Policy Update Complete")
        print("=" * 60)
        print(f"\nCloudFront can now access:")
        print(f"  s3://{BUCKET_NAME}/web-ui/*")
        print(f"\nTest your application:")
        print(f"  https://d3v7khazsfb4vd.cloudfront.net")
        print("\n⏳ Wait 2-3 minutes for changes to propagate")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Failed to update bucket policy: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    fix_bucket_policy()
