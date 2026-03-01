#!/usr/bin/env python3
"""
Enable Amazon Nova Model Access in Bedrock
"""

import boto3
import sys

def enable_model_access(region='ap-south-1'):
    """Enable access to Amazon Nova models"""
    
    print(f"Enabling Amazon Nova model access in {region}...")
    
    # Note: Model access must be requested through AWS Console
    # This script provides instructions
    
    print("\n" + "="*60)
    print("IMPORTANT: Model Access Must Be Enabled in AWS Console")
    print("="*60)
    
    print(f"""
To enable Amazon Nova model access:

1. Go to AWS Console: https://console.aws.amazon.com/bedrock/
2. Select region: {region} (Mumbai)
3. Click "Model access" in the left sidebar
4. Click "Manage model access" button
5. Find "Amazon Nova" models and check:
   ✓ Amazon Nova Micro
   ✓ Amazon Nova Lite  
   ✓ Amazon Nova Pro
6. Scroll down and click "Request model access"
7. Wait 2-5 minutes for access to be granted

Current available models in {region}:
""")
    
    try:
        bedrock = boto3.client('bedrock', region_name=region)
        response = bedrock.list_foundation_models()
        
        nova_models = [m for m in response['modelSummaries'] if 'nova' in m['modelId'].lower()]
        
        for model in nova_models:
            print(f"  - {model['modelId']}")
            print(f"    Status: {model.get('modelLifecycle', {}).get('status', 'UNKNOWN')}")
            print(f"    Inference: {', '.join(model.get('inferenceTypesSupported', []))}")
            print()
        
        print("\nAfter enabling access, test with:")
        print(f"  aws bedrock-runtime invoke-model \\")
        print(f"    --region {region} \\")
        print(f"    --model-id amazon.nova-lite-v1:0 \\")
        print(f"    --body '{{\"messages\":[{{\"role\":\"user\",\"content\":\"Hello\"}}]}}' \\")
        print(f"    output.json")
        
    except Exception as e:
        print(f"\nError checking models: {e}")
        print("\nYou may need to enable Bedrock service first.")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    region = sys.argv[1] if len(sys.argv) > 1 else 'ap-south-1'
    enable_model_access(region)
