#!/usr/bin/env python3
"""
Create IAM policy to allow Lambda environment variable updates
"""

import boto3
import json
from botocore.exceptions import ClientError

def create_policy():
    """Create IAM policy for Lambda updates"""
    
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "lambda:GetFunctionConfiguration",
                    "lambda:UpdateFunctionConfiguration"
                ],
                "Resource": "arn:aws:lambda:ap-south-1:188238313375:function/ure-lambda-function"
            }
        ]
    }
    
    print("=" * 60)
    print("Creating IAM Policy for Lambda Updates")
    print("=" * 60)
    print()
    
    print("📋 Policy Document:")
    print(json.dumps(policy_document, indent=2))
    print()
    
    try:
        iam = boto3.client('iam')
        
        policy_name = 'LambdaEnvironmentUpdatePolicy'
        
        print(f"🔧 Creating policy: {policy_name}")
        
        response = iam.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document),
            Description='Allow updating Lambda environment variables for URE function'
        )
        
        policy_arn = response['Policy']['Arn']
        
        print(f"✅ Policy created successfully!")
        print(f"   ARN: {policy_arn}")
        print()
        
        # Attach to root user (if possible)
        print("🔗 Attempting to attach policy to current user...")
        
        try:
            sts = boto3.client('sts')
            identity = sts.get_caller_identity()
            
            if ':root' in identity['Arn']:
                print("⚠️  Cannot attach policy to root user via API")
                print("   Root user has all permissions by default")
                print()
                print("   The issue is likely that root user needs to:")
                print("   1. Enable Bedrock model access first")
                print("   2. Or use an IAM user instead of root")
                print()
            else:
                # Try to attach to current user
                user_name = identity['Arn'].split('/')[-1]
                iam.attach_user_policy(
                    UserName=user_name,
                    PolicyArn=policy_arn
                )
                print(f"✅ Policy attached to user: {user_name}")
                print()
        
        except Exception as e:
            print(f"⚠️  Could not attach policy: {str(e)}")
            print()
        
        print("=" * 60)
        print("Manual Steps Required:")
        print("=" * 60)
        print()
        print("Since you're using root account with restrictions,")
        print("you need to enable Bedrock model access first:")
        print()
        print("1. Go to Bedrock Console:")
        print("   https://ap-south-1.console.aws.amazon.com/bedrock/")
        print()
        print("2. Click 'Playgrounds' in left sidebar")
        print()
        print("3. Click 'Chat' playground")
        print()
        print("4. Select 'Amazon Nova Lite' from model dropdown")
        print()
        print("5. Type 'Hello' and click 'Run'")
        print("   (This will auto-enable the model)")
        print()
        print("6. Then update Lambda env var manually or via CLI")
        print()
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        
        if error_code == 'EntityAlreadyExists':
            print(f"✅ Policy already exists: {policy_name}")
            print()
        else:
            print(f"❌ Error: {error_code}")
            print(f"   Message: {e.response['Error']['Message']}")
            print()


if __name__ == "__main__":
    create_policy()
