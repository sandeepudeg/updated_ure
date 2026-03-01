#!/usr/bin/env python3
"""
Update Lambda Environment Variable using AWS CLI
Workaround for console permission issues
"""

import boto3
import json
from botocore.exceptions import ClientError

def update_lambda_env():
    """Update Lambda environment variable"""
    
    region = 'ap-south-1'
    function_name = 'ure-lambda-function'
    
    print("=" * 60)
    print("Updating Lambda Environment Variable")
    print(f"Function: {function_name}")
    print(f"Region: {region}")
    print("=" * 60)
    print()
    
    try:
        lambda_client = boto3.client('lambda', region_name=region)
        
        # Get current configuration
        print("📥 Fetching current configuration...")
        response = lambda_client.get_function_configuration(
            FunctionName=function_name
        )
        
        current_env = response.get('Environment', {}).get('Variables', {})
        
        print(f"✅ Current BEDROCK_MODEL_ID: {current_env.get('BEDROCK_MODEL_ID', 'NOT SET')}")
        print(f"✅ Current BEDROCK_REGION: {current_env.get('BEDROCK_REGION', 'NOT SET')}")
        print()
        
        # Update environment variables
        current_env['BEDROCK_MODEL_ID'] = 'amazon.nova-lite-v1:0'
        current_env['BEDROCK_REGION'] = 'ap-south-1'
        
        print("🔄 Updating environment variables...")
        print(f"   New BEDROCK_MODEL_ID: amazon.nova-lite-v1:0")
        print(f"   New BEDROCK_REGION: ap-south-1")
        print()
        
        update_response = lambda_client.update_function_configuration(
            FunctionName=function_name,
            Environment={
                'Variables': current_env
            }
        )
        
        print("✅ SUCCESS! Lambda environment variables updated")
        print()
        print("=" * 60)
        print("Next Steps:")
        print("=" * 60)
        print()
        print("1. Wait 10-15 seconds for Lambda to update")
        print()
        print("2. Run Streamlit app:")
        print("   .\\run_streamlit.ps1")
        print()
        print("3. Test with a query in the app")
        print()
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        
        print(f"❌ Error: {error_code}")
        print(f"   Message: {error_msg}")
        print()
        
        if error_code == 'ResourceNotFoundException':
            print("⚠️  Lambda function not found")
            print(f"   Function name: {function_name}")
            print(f"   Region: {region}")
            print()
            print("   Please verify the function name and region are correct")
            print()
        
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


if __name__ == "__main__":
    update_lambda_env()
