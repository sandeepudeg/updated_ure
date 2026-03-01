#!/usr/bin/env python3
"""
Enable Amazon Nova Model by First Invocation
AWS now auto-enables models on first use
"""

import boto3
from botocore.exceptions import ClientError

def test_and_enable_model():
    """Test Nova model and enable it by invoking"""
    
    region = 'ap-south-1'
    model_id = 'amazon.nova-lite-v1:0'
    
    print("=" * 60)
    print("Testing Amazon Nova Model Access")
    print(f"Region: {region}")
    print(f"Model: {model_id}")
    print("=" * 60)
    print()
    
    try:
        bedrock_runtime = boto3.client('bedrock-runtime', region_name=region)
        
        print("🧪 Invoking model for the first time...")
        print("   (This will auto-enable the model if not already enabled)")
        print()
        
        # Simple test invocation
        response = bedrock_runtime.converse(
            modelId=model_id,
            messages=[{
                "role": "user",
                "content": [{"text": "Hello, respond with just 'Hi'"}]
            }]
        )
        
        response_text = response['output']['message']['content'][0]['text']
        
        print("✅ SUCCESS! Model is now enabled and working!")
        print()
        print(f"Test Response: {response_text}")
        print()
        print("=" * 60)
        print("Next Steps:")
        print("=" * 60)
        print()
        print("1. Update Lambda environment variable:")
        print(f"   BEDROCK_MODEL_ID = {model_id}")
        print()
        print("2. Go to Lambda Console:")
        print("   https://ap-south-1.console.aws.amazon.com/lambda/home?region=ap-south-1#/functions/ure-lambda-function")
        print()
        print("3. Configuration → Environment variables → Edit")
        print()
        print("4. Change BEDROCK_MODEL_ID from:")
        print("   apac.amazon.nova-lite-v1:0")
        print("   to:")
        print(f"   {model_id}")
        print()
        print("5. Save and test your Streamlit app")
        print()
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        
        print(f"❌ Error: {error_code}")
        print(f"   Message: {error_msg}")
        print()
        
        if 'AccessDeniedException' in error_code:
            print("🔐 Access Denied")
            print("   Your IAM user/role may not have permission to invoke Bedrock models")
            print()
            print("   Required IAM permissions:")
            print("   - bedrock:InvokeModel")
            print("   - bedrock:InvokeModelWithResponseStream")
            print()
        elif 'ValidationException' in error_code:
            print("⚠️  Model validation error")
            print("   The model may need to be invoked by an admin first")
            print()
        
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


if __name__ == "__main__":
    test_and_enable_model()
