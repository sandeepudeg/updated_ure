#!/usr/bin/env python3
"""
Check Bedrock Model Access Status in Mumbai Region
"""

import boto3
from botocore.exceptions import ClientError

def check_model_access():
    """Check which Bedrock models are accessible"""
    
    region = 'ap-south-1'
    
    print("=" * 60)
    print("Checking Bedrock Model Access")
    print(f"Region: {region}")
    print("=" * 60)
    print()
    
    try:
        bedrock = boto3.client('bedrock', region_name=region)
        
        # List foundation models
        print("📋 Listing available foundation models...")
        response = bedrock.list_foundation_models()
        
        # Filter for Amazon Nova models
        nova_models = [
            model for model in response['modelSummaries']
            if 'nova' in model['modelId'].lower()
        ]
        
        if nova_models:
            print(f"\n✅ Found {len(nova_models)} Amazon Nova models:\n")
            for model in nova_models:
                model_id = model['modelId']
                model_name = model.get('modelName', 'N/A')
                status = model.get('modelLifecycle', {}).get('status', 'UNKNOWN')
                
                print(f"  • {model_name}")
                print(f"    Model ID: {model_id}")
                print(f"    Status: {status}")
                print()
        else:
            print("\n❌ No Amazon Nova models found")
            print("You may need to enable model access in the Bedrock console")
            print()
        
        # Try to test model access by calling Bedrock Runtime
        print("🧪 Testing model access with Bedrock Runtime...")
        bedrock_runtime = boto3.client('bedrock-runtime', region_name=region)
        
        test_model_id = 'amazon.nova-lite-v1:0'
        
        try:
            # Try a simple converse call
            response = bedrock_runtime.converse(
                modelId=test_model_id,
                messages=[{
                    "role": "user",
                    "content": [{"text": "Hello"}]
                }]
            )
            
            print(f"✅ SUCCESS! Model {test_model_id} is accessible")
            print(f"   Response: {response['output']['message']['content'][0]['text'][:50]}...")
            print()
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = e.response['Error']['Message']
            
            if error_code == 'ValidationException' and 'Operation not allowed' in error_msg:
                print(f"❌ Model access NOT enabled for {test_model_id}")
                print("   You need to enable model access in Bedrock console")
                print()
                print("   Steps:")
                print("   1. Go to: https://console.aws.amazon.com/bedrock/")
                print("   2. Select region: ap-south-1")
                print("   3. Click 'Model access' → 'Manage model access'")
                print("   4. Check boxes for Amazon Nova models")
                print("   5. Click 'Request model access'")
                print()
            else:
                print(f"❌ Error testing model: {error_code}")
                print(f"   Message: {error_msg}")
                print()
        
    except ClientError as e:
        print(f"❌ Error: {e.response['Error']['Code']}")
        print(f"   Message: {e.response['Error']['Message']}")
        print()
    
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        print()
    
    print("=" * 60)


if __name__ == "__main__":
    check_model_access()
