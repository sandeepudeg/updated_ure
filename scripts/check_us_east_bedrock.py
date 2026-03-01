#!/usr/bin/env python3
"""Check Bedrock in us-east-1"""

import boto3
from botocore.exceptions import ClientError

region = 'us-east-1'
model_id = 'us.amazon.nova-pro-v1:0'

print(f"Testing Bedrock in {region}")
print(f"Model: {model_id}")
print()

try:
    bedrock_runtime = boto3.client('bedrock-runtime', region_name=region)
    
    response = bedrock_runtime.converse(
        modelId=model_id,
        messages=[{
            "role": "user",
            "content": [{"text": "Hello"}]
        }]
    )
    
    print("✅ SUCCESS! Model is working")
    print(f"Response: {response['output']['message']['content'][0]['text']}")
    
except ClientError as e:
    print(f"❌ Error: {e.response['Error']['Code']}")
    print(f"Message: {e.response['Error']['Message']}")
