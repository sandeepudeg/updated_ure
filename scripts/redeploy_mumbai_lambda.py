#!/usr/bin/env python3
"""
Redeploy Mumbai Lambda with updated code (nova-lite model)
"""

import boto3
import zipfile
import os
import time
from pathlib import Path

# Configuration
REGION = 'ap-south-1'
FUNCTION_NAME = 'ure-mvp-handler-mumbai'
LAMBDA_ROLE_ARN = 'arn:aws:iam::188238313375:role/ure-lambda-role'

def create_deployment_package():
    """Create Lambda deployment package"""
    print("=" * 60)
    print("Creating Lambda Deployment Package")
    print("=" * 60)
    print()
    
    # Create zip file
    zip_path = 'lambda_deployment.zip'
    
    print("Creating ZIP file...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add Lambda handler
        print("  Adding lambda_handler.py...")
        zipf.write('src/aws/lambda_handler.py', 'lambda_handler.py')
        
        # Add agents
        print("  Adding agents...")
        for agent_file in Path('src/agents').glob('*.py'):
            if agent_file.name != '__pycache__':
                zipf.write(agent_file, f'agents/{agent_file.name}')
        
        # Add utils
        print("  Adding utils...")
        for util_file in Path('src/utils').glob('*.py'):
            if util_file.name != '__pycache__':
                zipf.write(util_file, f'utils/{util_file.name}')
        
        # Add MCP client
        print("  Adding MCP client...")
        for mcp_file in Path('src/mcp').glob('*.py'):
            if mcp_file.name != '__pycache__':
                zipf.write(mcp_file, f'mcp/{mcp_file.name}')
    
    file_size = os.path.getsize(zip_path) / 1024 / 1024
    print(f"✓ Deployment package created: {zip_path} ({file_size:.2f} MB)")
    print()
    
    return zip_path


def update_lambda_code(zip_path):
    """Update Lambda function code"""
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    print("=" * 60)
    print("Updating Lambda Function Code")
    print("=" * 60)
    print(f"Function: {FUNCTION_NAME}")
    print(f"Region: {REGION}")
    print()
    
    try:
        # Read zip file
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        print("Uploading new code...")
        response = lambda_client.update_function_code(
            FunctionName=FUNCTION_NAME,
            ZipFile=zip_content
        )
        
        print(f"✓ Code uploaded successfully")
        print(f"  Version: {response['Version']}")
        print(f"  Last Modified: {response['LastModified']}")
        print()
        
        # Wait for update to complete
        print("Waiting for Lambda to update...")
        waiter = lambda_client.get_waiter('function_updated')
        waiter.wait(FunctionName=FUNCTION_NAME)
        print("✓ Lambda update complete")
        print()
        
        return True
        
    except Exception as e:
        print(f"✗ Error updating Lambda code: {e}")
        return False


def update_environment_variables():
    """Update Lambda environment variables"""
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    print("=" * 60)
    print("Updating Environment Variables")
    print("=" * 60)
    print()
    
    try:
        # Get current configuration
        response = lambda_client.get_function_configuration(
            FunctionName=FUNCTION_NAME
        )
        
        current_env = response.get('Environment', {}).get('Variables', {})
        
        # Update model ID
        current_env['BEDROCK_MODEL_ID'] = 'amazon.nova-lite-v1:0'
        current_env['BEDROCK_REGION'] = REGION
        
        print("Setting environment variables:")
        print(f"  BEDROCK_MODEL_ID: amazon.nova-lite-v1:0")
        print(f"  BEDROCK_REGION: {REGION}")
        print()
        
        # Update
        lambda_client.update_function_configuration(
            FunctionName=FUNCTION_NAME,
            Environment={
                'Variables': current_env
            }
        )
        
        print("✓ Environment variables updated")
        print()
        
        # Wait for update
        print("Waiting for configuration update...")
        waiter = lambda_client.get_waiter('function_updated')
        waiter.wait(FunctionName=FUNCTION_NAME)
        print("✓ Configuration update complete")
        print()
        
        return True
        
    except Exception as e:
        print(f"✗ Error updating environment: {e}")
        return False


def test_lambda():
    """Test the Lambda function"""
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    print("=" * 60)
    print("Testing Lambda Function")
    print("=" * 60)
    print()
    
    import json
    
    test_event = {
        'user_id': 'test_user_001',
        'query': 'What are the symptoms of tomato late blight?',
        'language': 'en'
    }
    
    try:
        print(f"Test query: {test_event['query']}")
        print()
        
        response = lambda_client.invoke(
            FunctionName=FUNCTION_NAME,
            InvocationType='RequestResponse',
            Payload=json.dumps(test_event)
        )
        
        response_payload = json.loads(response['Payload'].read())
        
        if response['StatusCode'] == 200:
            body = json.loads(response_payload['body'])
            print(f"✓ Lambda test successful")
            print(f"Agent Used: {body.get('agent_used', 'unknown')}")
            print(f"Response: {body.get('response', '')[:200]}...")
            print()
            return True
        else:
            print(f"✗ Lambda test failed")
            print(f"Response: {response_payload}")
            print()
            return False
            
    except Exception as e:
        print(f"✗ Error testing Lambda: {e}")
        return False


def main():
    """Main execution"""
    print("\n" + "=" * 60)
    print("REDEPLOY MUMBAI LAMBDA WITH NOVA LITE")
    print("=" * 60)
    print()
    
    # Step 1: Create deployment package
    zip_path = create_deployment_package()
    
    # Step 2: Update Lambda code
    if not update_lambda_code(zip_path):
        print("Failed to update Lambda code. Exiting.")
        return
    
    # Step 3: Update environment variables
    if not update_environment_variables():
        print("Warning: Failed to update environment variables.")
    
    # Wait for changes to propagate
    print("Waiting 5 seconds for changes to propagate...")
    time.sleep(5)
    print()
    
    # Step 4: Test Lambda
    if not test_lambda():
        print("Warning: Lambda test failed. Check CloudWatch logs.")
    
    # Cleanup
    print("Cleaning up...")
    if os.path.exists(zip_path):
        os.remove(zip_path)
        print(f"✓ Removed {zip_path}")
    print()
    
    print("=" * 60)
    print("REDEPLOYMENT COMPLETE")
    print("=" * 60)
    print()
    print("Summary:")
    print(f"  - Function: {FUNCTION_NAME}")
    print(f"  - Region: {REGION}")
    print(f"  - Model: amazon.nova-lite-v1:0")
    print()
    print("API Endpoint:")
    print("  https://3dcqel7asa.execute-api.ap-south-1.amazonaws.com/prod/query")
    print()
    print("Next steps:")
    print("  1. Test with Streamlit app")
    print("  2. Monitor CloudWatch logs")
    print("  3. Check API Gateway metrics")
    print()


if __name__ == "__main__":
    main()
