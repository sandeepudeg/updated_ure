#!/usr/bin/env python3
"""
Quick Lambda Update - Only update code, skip dependencies
"""

import boto3
import zipfile
import os
import time
from pathlib import Path

FUNCTION_NAME = "ure-mvp-handler"
REGION = "us-east-1"

def create_code_only_zip():
    """Create zip with only source code (no dependencies)"""
    print("Creating code-only deployment package...")
    
    zip_path = "lambda_code_only.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add Lambda handler
        zipf.write('src/aws/lambda_handler.py', 'lambda_handler.py')
        
        # Add agents
        for agent_file in Path('src/agents').glob('*.py'):
            zipf.write(agent_file, f'agents/{agent_file.name}')
        
        # Add utils
        for util_file in Path('src/utils').glob('*.py'):
            zipf.write(util_file, f'utils/{util_file.name}')
        
        # Add MCP client
        for mcp_file in Path('src/mcp').glob('*.py'):
            zipf.write(mcp_file, f'mcp/{mcp_file.name}')
    
    size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"✓ Created: {zip_path} ({size_mb:.2f} MB)")
    
    return zip_path

def wait_for_lambda_ready(client, function_name, max_wait=300):
    """Wait for Lambda function to be ready for updates"""
    print("Waiting for Lambda function to be ready...")
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            response = client.get_function(FunctionName=function_name)
            state = response['Configuration']['State']
            last_update_status = response['Configuration']['LastUpdateStatus']
            
            if state == 'Active' and last_update_status in ['Successful', 'Failed']:
                print(f"✓ Lambda is ready (State: {state}, Status: {last_update_status})")
                return True
            
            print(f"  Waiting... (State: {state}, Status: {last_update_status})")
            time.sleep(5)
        except Exception as e:
            print(f"  Error checking status: {e}")
            time.sleep(5)
    
    print(f"✗ Timeout waiting for Lambda to be ready")
    return False

def update_lambda_code():
    """Update Lambda function code only"""
    print("=" * 60)
    print("Quick Lambda Code Update")
    print("=" * 60)
    
    # Create zip
    zip_path = create_code_only_zip()
    
    # Initialize boto3 client
    client = boto3.client('lambda', region_name=REGION)
    
    # Wait for Lambda to be ready
    if not wait_for_lambda_ready(client, FUNCTION_NAME):
        print("\n⚠ Lambda is still updating. Please wait and try again.")
        return False
    
    # Read zip file
    print(f"\nUploading code to Lambda...")
    with open(zip_path, 'rb') as f:
        zip_content = f.read()
    
    try:
        # Update function code
        response = client.update_function_code(
            FunctionName=FUNCTION_NAME,
            ZipFile=zip_content,
            Publish=True
        )
        
        print(f"✓ Lambda code updated successfully")
        print(f"  Function: {response['FunctionName']}")
        print(f"  Version: {response['Version']}")
        print(f"  State: {response['State']}")
        print(f"  Last Modified: {response['LastModified']}")
        
        # Clean up
        os.remove(zip_path)
        
        print("\n" + "=" * 60)
        print("Update Complete")
        print("=" * 60)
        print("\n✓ Lambda function updated with latest code")
        print("✓ Guardrails disabled for agricultural queries")
        print("✓ Location context now included in queries")
        print("\nTest your application:")
        print("  https://d3v7khazsfb4vd.cloudfront.net")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Failed to update Lambda: {e}")
        return False

if __name__ == "__main__":
    update_lambda_code()
