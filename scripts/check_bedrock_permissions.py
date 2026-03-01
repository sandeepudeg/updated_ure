#!/usr/bin/env python3
"""
Check IAM Permissions for Bedrock
"""

import boto3
from botocore.exceptions import ClientError

def check_permissions():
    """Check current IAM permissions for Bedrock"""
    
    print("=" * 60)
    print("Checking IAM Permissions for Bedrock")
    print("=" * 60)
    print()
    
    try:
        # Get current identity
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        print("📋 Current AWS Identity:")
        print(f"   Account: {identity['Account']}")
        print(f"   User ARN: {identity['Arn']}")
        print(f"   User ID: {identity['UserId']}")
        print()
        
        # Check if root user
        if ':root' in identity['Arn']:
            print("⚠️  You are using ROOT account")
            print("   Root accounts may have restrictions on some Bedrock operations")
            print()
        
        # Try to list Bedrock models (requires bedrock:ListFoundationModels)
        print("🔍 Testing Bedrock permissions...")
        print()
        
        bedrock = boto3.client('bedrock', region_name='ap-south-1')
        
        try:
            response = bedrock.list_foundation_models()
            print("✅ bedrock:ListFoundationModels - ALLOWED")
        except ClientError as e:
            print(f"❌ bedrock:ListFoundationModels - DENIED ({e.response['Error']['Code']})")
        
        # Try to invoke model (requires bedrock:InvokeModel)
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='ap-south-1')
        
        try:
            # This will fail if model not enabled, but we can check the error
            response = bedrock_runtime.converse(
                modelId='amazon.nova-lite-v1:0',
                messages=[{"role": "user", "content": [{"text": "test"}]}]
            )
            print("✅ bedrock:InvokeModel - ALLOWED (model enabled)")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AccessDeniedException':
                print("❌ bedrock:InvokeModel - DENIED (no permission)")
            elif error_code == 'ValidationException':
                print("⚠️  bedrock:InvokeModel - ALLOWED (but model not enabled)")
                print("   Error: Operation not allowed")
                print()
                print("   This means:")
                print("   - You have permission to invoke models")
                print("   - But the model is not enabled for your account")
                print()
                print("   SOLUTION: Use AWS Console to enable model")
                print("   1. Go to: https://console.aws.amazon.com/bedrock/")
                print("   2. Select region: ap-south-1")
                print("   3. Click 'Model catalog' in left sidebar")
                print("   4. Search for 'Nova Lite'")
                print("   5. Click on the model")
                print("   6. Click 'Enable model' or 'Request access' button")
            else:
                print(f"⚠️  bedrock:InvokeModel - ERROR ({error_code})")
        
        print()
        print("=" * 60)
        print("Recommendation:")
        print("=" * 60)
        print()
        print("Since you're using root account, you need to:")
        print()
        print("1. Go to Bedrock Console:")
        print("   https://ap-south-1.console.aws.amazon.com/bedrock/home?region=ap-south-1")
        print()
        print("2. Click 'Model catalog' in the left sidebar")
        print()
        print("3. Search for 'Amazon Nova Lite'")
        print()
        print("4. Click on the model card")
        print()
        print("5. Look for 'Enable model' or 'Use in Playground' button")
        print()
        print("6. Click it to enable the model for your account")
        print()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print()


if __name__ == "__main__":
    check_permissions()
