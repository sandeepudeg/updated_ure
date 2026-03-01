#!/usr/bin/env python3
"""
Update Mumbai Lambda to use amazon.nova-lite-v1:0 model
"""

import boto3
import json
import time

# Configuration
REGION = 'ap-south-1'
FUNCTION_NAME = 'ure-mvp-handler-mumbai'
NEW_MODEL_ID = 'amazon.nova-lite-v1:0'

def update_lambda_environment():
    """Update Lambda environment variable for model ID"""
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    print("=" * 60)
    print("Updating Lambda Environment Variable")
    print("=" * 60)
    print(f"Function: {FUNCTION_NAME}")
    print(f"Region: {REGION}")
    print(f"New Model ID: {NEW_MODEL_ID}")
    print()
    
    try:
        # Get current configuration
        print("Getting current Lambda configuration...")
        response = lambda_client.get_function_configuration(
            FunctionName=FUNCTION_NAME
        )
        
        current_env = response.get('Environment', {}).get('Variables', {})
        old_model_id = current_env.get('BEDROCK_MODEL_ID', 'Not set')
        
        print(f"Current Model ID: {old_model_id}")
        print()
        
        # Update environment variable
        print("Updating environment variable...")
        current_env['BEDROCK_MODEL_ID'] = NEW_MODEL_ID
        
        update_response = lambda_client.update_function_configuration(
            FunctionName=FUNCTION_NAME,
            Environment={
                'Variables': current_env
            }
        )
        
        print(f"✓ Environment variable updated")
        print(f"  Old: {old_model_id}")
        print(f"  New: {NEW_MODEL_ID}")
        print()
        
        # Wait for update to complete
        print("Waiting for Lambda to update...")
        waiter = lambda_client.get_waiter('function_updated')
        waiter.wait(FunctionName=FUNCTION_NAME)
        print("✓ Lambda update complete")
        print()
        
        return True
        
    except Exception as e:
        print(f"✗ Error updating Lambda: {e}")
        return False


def test_model_invocation():
    """Test the model with a simple invocation"""
    bedrock_runtime = boto3.client('bedrock-runtime', region_name=REGION)
    
    print("=" * 60)
    print("Testing Model Invocation")
    print("=" * 60)
    print(f"Model: {NEW_MODEL_ID}")
    print(f"Region: {REGION}")
    print()
    
    try:
        print("Sending test request...")
        response = bedrock_runtime.converse(
            modelId=NEW_MODEL_ID,
            messages=[{
                "role": "user",
                "content": [{"text": "Hello, can you help farmers?"}]
            }]
        )
        
        response_text = response['output']['message']['content'][0]['text']
        print(f"✓ Model responded successfully")
        print(f"Response: {response_text[:100]}...")
        print()
        
        return True
        
    except Exception as e:
        print(f"✗ Error invoking model: {e}")
        print()
        return False


def test_lambda_function():
    """Test the Lambda function with the new model"""
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    print("=" * 60)
    print("Testing Lambda Function")
    print("=" * 60)
    print(f"Function: {FUNCTION_NAME}")
    print()
    
    # Test payload
    test_event = {
        'user_id': 'test_user_001',
        'query': 'What are the symptoms of tomato late blight?',
        'language': 'en'
    }
    
    try:
        print("Invoking Lambda function...")
        print(f"Test query: {test_event['query']}")
        print()
        
        response = lambda_client.invoke(
            FunctionName=FUNCTION_NAME,
            InvocationType='RequestResponse',
            Payload=json.dumps(test_event)
        )
        
        # Parse response
        response_payload = json.loads(response['Payload'].read())
        
        if response['StatusCode'] == 200:
            body = json.loads(response_payload['body'])
            print(f"✓ Lambda invocation successful")
            print(f"Status Code: {response_payload['statusCode']}")
            print(f"Agent Used: {body.get('agent_used', 'unknown')}")
            print(f"Response: {body.get('response', '')[:200]}...")
            print()
            return True
        else:
            print(f"✗ Lambda returned error")
            print(f"Status Code: {response['StatusCode']}")
            print(f"Response: {response_payload}")
            print()
            return False
            
    except Exception as e:
        print(f"✗ Error invoking Lambda: {e}")
        print()
        return False


def main():
    """Main execution"""
    print("\n" + "=" * 60)
    print("UPDATE MUMBAI LAMBDA TO NOVA LITE MODEL")
    print("=" * 60)
    print()
    
    # Step 1: Update Lambda environment
    if not update_lambda_environment():
        print("Failed to update Lambda environment. Exiting.")
        return
    
    # Wait a bit for changes to propagate
    print("Waiting 5 seconds for changes to propagate...")
    time.sleep(5)
    print()
    
    # Step 2: Test model directly
    if not test_model_invocation():
        print("Warning: Direct model invocation failed.")
        print("This might be a permissions issue.")
        print()
    
    # Step 3: Test Lambda function
    if not test_lambda_function():
        print("Warning: Lambda function test failed.")
        print("Check CloudWatch logs for details.")
        print()
    
    print("=" * 60)
    print("UPDATE COMPLETE")
    print("=" * 60)
    print()
    print("Summary:")
    print(f"  - Lambda function: {FUNCTION_NAME}")
    print(f"  - Region: {REGION}")
    print(f"  - Model ID: {NEW_MODEL_ID}")
    print()
    print("Next steps:")
    print("  1. Test the API endpoint with a real query")
    print("  2. Check CloudWatch logs if issues occur")
    print("  3. Verify model access in Bedrock console")
    print()


if __name__ == "__main__":
    main()
