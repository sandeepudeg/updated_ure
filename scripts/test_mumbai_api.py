#!/usr/bin/env python3
"""
Test Mumbai API Gateway endpoint
"""

import requests
import json
import time

API_ENDPOINT = 'https://3dcqel7asa.execute-api.ap-south-1.amazonaws.com/prod/query'

def test_api():
    """Test the API with a simple query"""
    print("=" * 60)
    print("TESTING MUMBAI API")
    print("=" * 60)
    print(f"Endpoint: {API_ENDPOINT}")
    print()
    
    # Test payload
    payload = {
        'user_id': 'test_user_001',
        'query': 'Hello, can you help farmers?',
        'language': 'en'
    }
    
    print("Sending test request...")
    print(f"Query: {payload['query']}")
    print()
    
    try:
        start_time = time.time()
        
        response = requests.post(
            API_ENDPOINT,
            json=payload,
            timeout=30
        )
        
        elapsed_time = time.time() - start_time
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Time: {elapsed_time:.2f}s")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print("✓ API call successful")
            print()
            print("Response:")
            print(f"  Agent Used: {data.get('agent_used', 'unknown')}")
            print(f"  Response: {data.get('response', '')[:200]}...")
            print()
            return True
            
        else:
            print(f"✗ API call failed")
            print()
            print("Error Response:")
            print(response.text)
            print()
            
            if response.status_code == 502:
                print("502 Bad Gateway - Lambda function error")
                print()
                print("Possible causes:")
                print("  1. Lambda function crashed")
                print("  2. Lambda timeout")
                print("  3. Bedrock model access error")
                print("  4. Missing dependencies")
                print()
                print("Next steps:")
                print("  1. Check Lambda logs: py scripts/check_lambda_logs.py")
                print("  2. Redeploy Lambda: py scripts/redeploy_mumbai_lambda.py")
                print()
            
            return False
            
    except requests.exceptions.Timeout:
        print("✗ Request timed out")
        print()
        print("Lambda might be taking too long to respond")
        print("Check CloudWatch logs for details")
        print()
        return False
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print()
        return False


def main():
    """Main execution"""
    print("\n" + "=" * 60)
    print("MUMBAI API TEST")
    print("=" * 60)
    print()
    
    success = test_api()
    
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print()
    
    if success:
        print("✓ API is working correctly")
        print()
        print("You can now use the Streamlit app:")
        print("  .\\run_local_with_logging.ps1")
        print()
    else:
        print("✗ API test failed")
        print()
        print("Troubleshooting steps:")
        print("  1. Check Lambda logs:")
        print("     py scripts/check_lambda_logs.py")
        print()
        print("  2. Redeploy Lambda with updated code:")
        print("     py scripts/redeploy_mumbai_lambda.py")
        print()
        print("  3. Check Bedrock model access:")
        print("     - Go to AWS Bedrock console")
        print("     - Verify amazon.nova-lite-v1:0 is enabled")
        print()


if __name__ == "__main__":
    main()
