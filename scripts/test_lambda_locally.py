#!/usr/bin/env python3
"""
Local Lambda Handler Testing Script
Tests the Lambda handler with mock events before deployment
"""

import json
import sys
import os
from pathlib import Path

# Add src to path
src_path = str(Path(__file__).parent.parent / 'src')
sys.path.insert(0, src_path)

# Mock AWS environment variables for local testing
os.environ['DYNAMODB_TABLE_NAME'] = 'ure-conversations'
os.environ['DYNAMODB_USER_TABLE'] = 'ure-user-profiles'
os.environ['S3_BUCKET_NAME'] = 'ure-mvp-data-us-east-1-188238313375'
os.environ['LOG_LEVEL'] = 'INFO'
os.environ['IP_HASH_SALT'] = 'test-salt-for-local-testing'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

# Import after setting env vars
from aws.lambda_handler import lambda_handler


def test_basic_query():
    """Test basic text query"""
    print("\n" + "="*60)
    print("TEST 1: Basic Text Query")
    print("="*60)
    
    event = {
        'user_id': 'test_farmer_001',
        'query': 'What are the symptoms of tomato late blight?',
        'language': 'en'
    }
    
    try:
        result = lambda_handler(event, None)
        print(f"Status Code: {result['statusCode']}")
        
        if result['statusCode'] == 200:
            body = json.loads(result['body'])
            print(f"Agent Used: {body.get('agent_used')}")
            print(f"Response Preview: {body.get('response')[:200]}...")
            print("✅ Test PASSED")
        else:
            print(f"❌ Test FAILED: {result['body']}")
            
        return result['statusCode'] == 200
    except Exception as e:
        print(f"❌ Test FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_location():
    """Test query with location context"""
    print("\n" + "="*60)
    print("TEST 2: Query with Location Context")
    print("="*60)
    
    event = {
        'user_id': 'test_farmer_002',
        'query': 'What crops should I plant this season?',
        'language': 'en',
        'location': 'Maharashtra, India'
    }
    
    try:
        result = lambda_handler(event, None)
        print(f"Status Code: {result['statusCode']}")
        
        if result['statusCode'] == 200:
            body = json.loads(result['body'])
            print(f"Agent Used: {body.get('agent_used')}")
            print(f"Response Preview: {body.get('response')[:200]}...")
            print("✅ Test PASSED")
        else:
            print(f"❌ Test FAILED: {result['body']}")
            
        return result['statusCode'] == 200
    except Exception as e:
        print(f"❌ Test FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_gateway_format():
    """Test with API Gateway event format"""
    print("\n" + "="*60)
    print("TEST 3: API Gateway Event Format")
    print("="*60)
    
    event = {
        'body': json.dumps({
            'user_id': 'test_farmer_003',
            'query': 'How do I apply for PM-Kisan scheme?',
            'language': 'en'
        }),
        'requestContext': {
            'identity': {
                'sourceIp': '192.168.1.100'
            }
        }
    }
    
    try:
        result = lambda_handler(event, None)
        print(f"Status Code: {result['statusCode']}")
        
        if result['statusCode'] == 200:
            body = json.loads(result['body'])
            print(f"Agent Used: {body.get('agent_used')}")
            print(f"Response Preview: {body.get('response')[:200]}...")
            
            # Check if IP was hashed
            metadata = body.get('metadata', {})
            print(f"Metadata keys: {list(metadata.keys())}")
            print("✅ Test PASSED")
        else:
            print(f"❌ Test FAILED: {result['body']}")
            
        return result['statusCode'] == 200
    except Exception as e:
        print(f"❌ Test FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_missing_parameters():
    """Test error handling for missing parameters"""
    print("\n" + "="*60)
    print("TEST 4: Missing Parameters (Error Handling)")
    print("="*60)
    
    event = {
        'user_id': 'test_farmer_004'
        # Missing 'query' parameter
    }
    
    try:
        result = lambda_handler(event, None)
        print(f"Status Code: {result['statusCode']}")
        
        if result['statusCode'] == 400:
            body = json.loads(result['body'])
            print(f"Error Message: {body.get('error')}")
            print("✅ Test PASSED (correctly rejected invalid input)")
        else:
            print(f"❌ Test FAILED: Expected 400, got {result['statusCode']}")
            
        return result['statusCode'] == 400
    except Exception as e:
        print(f"❌ Test FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all local tests"""
    print("\n" + "="*60)
    print("LAMBDA HANDLER LOCAL TESTING")
    print("="*60)
    print("\nNote: These tests will attempt to connect to AWS services.")
    print("Make sure your AWS credentials are configured.\n")
    
    tests = [
        test_basic_query,
        test_with_location,
        test_api_gateway_format,
        test_missing_parameters
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
