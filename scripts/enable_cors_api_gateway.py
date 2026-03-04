#!/usr/bin/env python3
"""
Enable CORS on API Gateway for CloudFront
"""

import boto3
import json

API_ID = "8938dqxf33"
RESOURCE_ID = "ptpki1"  # /query resource
REGION = "us-east-1"

def enable_cors():
    """Enable CORS on API Gateway"""
    
    client = boto3.client('apigateway', region_name=REGION)
    
    print("=" * 60)
    print("Enabling CORS on API Gateway")
    print("=" * 60)
    
    try:
        # Check if OPTIONS method exists
        print(f"\n1. Checking for OPTIONS method...")
        try:
            response = client.get_method(
                restApiId=API_ID,
                resourceId=RESOURCE_ID,
                httpMethod='OPTIONS'
            )
            print(f"✓ OPTIONS method already exists")
            options_exists = True
        except client.exceptions.NotFoundException:
            print(f"✗ OPTIONS method not found, will create it")
            options_exists = False
        
        if not options_exists:
            # Create OPTIONS method
            print(f"\n2. Creating OPTIONS method...")
            
            # Put method
            client.put_method(
                restApiId=API_ID,
                resourceId=RESOURCE_ID,
                httpMethod='OPTIONS',
                authorizationType='NONE'
            )
            
            # Put integration
            client.put_integration(
                restApiId=API_ID,
                resourceId=RESOURCE_ID,
                httpMethod='OPTIONS',
                type='MOCK',
                requestTemplates={
                    'application/json': '{"statusCode": 200}'
                }
            )
            
            # Put method response
            client.put_method_response(
                restApiId=API_ID,
                resourceId=RESOURCE_ID,
                httpMethod='OPTIONS',
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Headers': True,
                    'method.response.header.Access-Control-Allow-Methods': True,
                    'method.response.header.Access-Control-Allow-Origin': True
                },
                responseModels={
                    'application/json': 'Empty'
                }
            )
            
            # Put integration response
            client.put_integration_response(
                restApiId=API_ID,
                resourceId=RESOURCE_ID,
                httpMethod='OPTIONS',
                statusCode='200',
                responseParameters={
                    'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                    'method.response.header.Access-Control-Allow-Methods': "'GET,POST,PUT,DELETE,OPTIONS'",
                    'method.response.header.Access-Control-Allow-Origin': "'*'"
                },
                responseTemplates={
                    'application/json': ''
                }
            )
            
            print(f"✓ OPTIONS method created")
        
        # Update POST method response to include CORS headers
        print(f"\n3. Updating POST method response headers...")
        
        try:
            # Update method response
            client.update_method_response(
                restApiId=API_ID,
                resourceId=RESOURCE_ID,
                httpMethod='POST',
                statusCode='200',
                patchOperations=[
                    {
                        'op': 'add',
                        'path': '/responseParameters/method.response.header.Access-Control-Allow-Origin',
                        'value': 'true'
                    }
                ]
            )
            
            # Update integration response
            client.update_integration_response(
                restApiId=API_ID,
                resourceId=RESOURCE_ID,
                httpMethod='POST',
                statusCode='200',
                patchOperations=[
                    {
                        'op': 'add',
                        'path': '/responseParameters/method.response.header.Access-Control-Allow-Origin',
                        'value': "'*'"
                    }
                ]
            )
            
            print(f"✓ POST method CORS headers updated")
        except Exception as e:
            print(f"⚠ Could not update POST method: {e}")
            print(f"  This might be OK if headers already exist")
        
        # Deploy API
        print(f"\n4. Deploying API changes...")
        client.create_deployment(
            restApiId=API_ID,
            stageName='dev',
            description='Enable CORS for CloudFront'
        )
        
        print(f"✓ API deployed")
        
        print("\n" + "=" * 60)
        print("CORS Configuration Complete")
        print("=" * 60)
        print(f"\nCORS is now enabled on:")
        print(f"  https://{API_ID}.execute-api.{REGION}.amazonaws.com/dev/query")
        print(f"\nAllowed Origins: *")
        print(f"Allowed Methods: GET, POST, PUT, DELETE, OPTIONS")
        print(f"Allowed Headers: Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token")
        print(f"\n✓ Your web UI should now work!")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Failed to enable CORS: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    enable_cors()
