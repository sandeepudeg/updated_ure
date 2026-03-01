#!/usr/bin/env python3
"""
Update Mumbai Lambda Environment Variable for Bedrock Model ID
"""

import boto3
import json
from botocore.exceptions import ClientError

def update_lambda_model_id():
    """Update Lambda environment variable for Bedrock model ID"""
    
    # Configuration
    region = 'ap-south-1'
    function_name = 'ure-lambda-function'
    new_model_id = 'amazon.nova-lite-v1:0'  # Correct model ID for Mumbai region
    
    print(f"🔧 Updating Lambda function: {function_name}")
    print(f"📍 Region: {region}")
    print(f"🤖 New Model ID: {new_model_id}")
    print()
    
    try:
        # Initialize Lambda client
        lambda_client = boto3.client('lambda', region_name=region)
        
        # Get current function configuration
        print("📥 Fetching current configuration...")
        response = lambda_client.get_function_configuration(
            FunctionName=function_name
        )
        
        # Get current environment variables
        current_env = response.get('Environment', {}).get('Variables', {})
        print(f"✅ Current BEDROCK_MODEL_ID: {current_env.get('BEDROCK_MODEL_ID', 'NOT SET')}")
        print()
        
        # Update environment variables
        current_env['BEDROCK_MODEL_ID'] = new_model_id
        current_env['BEDROCK_REGION'] = region
        
        print("🔄 Updating Lambda environment variables...")
        update_response = lambda_client.update_function_configuration(
            FunctionName=function_name,
            Environment={
                'Variables': current_env
            }
        )
        
        print("✅ Lambda function updated successfully!")
        print()
        print(f"New configuration:")
        print(f"  BEDROCK_MODEL_ID: {new_model_id}")
        print(f"  BEDROCK_REGION: {region}")
        print()
        print("⏳ Wait 10-15 seconds for Lambda to update, then test your Streamlit app.")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        
        print(f"❌ Error: {error_code}")
        print(f"Message: {error_message}")
        print()
        
        if error_code == 'AccessDeniedException':
            print("🔐 Access Denied - Manual Update Required")
            print()
            print("Please update the Lambda environment variable manually:")
            print()
            print("1. Go to AWS Lambda Console:")
            print(f"   https://ap-south-1.console.aws.amazon.com/lambda/home?region=ap-south-1#/functions/{function_name}")
            print()
            print("2. Click 'Configuration' tab → 'Environment variables'")
            print()
            print("3. Click 'Edit'")
            print()
            print("4. Update or add these variables:")
            print(f"   BEDROCK_MODEL_ID = {new_model_id}")
            print(f"   BEDROCK_REGION = {region}")
            print()
            print("5. Click 'Save'")
            print()
        
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Mumbai Lambda - Bedrock Model ID Update")
    print("=" * 60)
    print()
    
    success = update_lambda_model_id()
    
    if success:
        print()
        print("=" * 60)
        print("✅ Update Complete!")
        print("=" * 60)
    else:
        print()
        print("=" * 60)
        print("⚠️  Manual Update Required")
        print("=" * 60)
