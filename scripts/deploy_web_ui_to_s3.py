#!/usr/bin/env python3
"""
Deploy GramSetu Web UI to S3 + CloudFront
"""

import boto3
import os
import mimetypes
from pathlib import Path
import json
import time

# Configuration
WEB_UI_DIR = 'src/web/aws-native'
S3_BUCKET_NAME = 'ure-mvp-data-us-east-1-188238313375'  # Use existing data bucket
WEB_UI_PREFIX = 'web-ui/'  # Prefix for web UI files in the bucket
CLOUDFRONT_COMMENT = 'GramSetu Web UI Distribution'

def create_s3_bucket(bucket_name, region='us-east-1'):
    """Create S3 bucket for website hosting (private, accessed via CloudFront OAI)"""
    s3_client = boto3.client('s3', region_name=region)
    
    try:
        # Check if bucket exists
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✓ Bucket {bucket_name} already exists")
        return True
    except:
        pass
    
    try:
        print(f"Creating S3 bucket: {bucket_name}")
        
        if region == 'us-east-1':
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        
        # Enable CORS (for API calls from the web UI)
        cors_configuration = {
            'CORSRules': [{
                'AllowedHeaders': ['*'],
                'AllowedMethods': ['GET', 'POST', 'PUT', 'DELETE', 'HEAD'],
                'AllowedOrigins': ['*'],
                'ExposeHeaders': ['ETag'],
                'MaxAgeSeconds': 3000
            }]
        }
        
        s3_client.put_bucket_cors(
            Bucket=bucket_name,
            CORSConfiguration=cors_configuration
        )
        
        print(f"✓ Bucket {bucket_name} created successfully (private, will use CloudFront OAI)")
        return True
        
    except Exception as e:
        print(f"✗ Failed to create bucket: {e}")
        return False


def upload_files_to_s3(bucket_name, source_dir, prefix=''):
    """Upload all files from source directory to S3 with optional prefix"""
    s3_client = boto3.client('s3')
    
    source_path = Path(source_dir)
    if not source_path.exists():
        print(f"✗ Source directory not found: {source_dir}")
        return False
    
    print(f"\nUploading files from {source_dir} to {bucket_name}/{prefix}...")
    
    uploaded_count = 0
    for file_path in source_path.rglob('*'):
        if file_path.is_file():
            # Get relative path
            relative_path = file_path.relative_to(source_path)
            s3_key = prefix + str(relative_path).replace('\\', '/')
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(str(file_path))
            if content_type is None:
                content_type = 'application/octet-stream'
            
            # Upload file
            try:
                extra_args = {'ContentType': content_type}
                
                # Set cache control for static assets
                if file_path.suffix in ['.js', '.css', '.html']:
                    extra_args['CacheControl'] = 'max-age=300'  # 5 minutes
                elif file_path.suffix in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico']:
                    extra_args['CacheControl'] = 'max-age=86400'  # 1 day
                
                s3_client.upload_file(
                    str(file_path),
                    bucket_name,
                    s3_key,
                    ExtraArgs=extra_args
                )
                
                print(f"  ✓ Uploaded: {s3_key}")
                uploaded_count += 1
                
            except Exception as e:
                print(f"  ✗ Failed to upload {s3_key}: {e}")
    
    print(f"\n✓ Uploaded {uploaded_count} files")
    return True


def create_cloudfront_distribution(bucket_name, prefix='', region='us-east-1'):
    """Create CloudFront distribution with OAI for S3 bucket"""
    cloudfront_client = boto3.client('cloudfront')
    s3_client = boto3.client('s3')
    
    print(f"\nCreating CloudFront distribution with Origin Access Identity...")
    
    try:
        # Check if distribution already exists
        distributions = cloudfront_client.list_distributions()
        
        if 'DistributionList' in distributions and 'Items' in distributions['DistributionList']:
            for dist in distributions['DistributionList']['Items']:
                if dist['Comment'] == CLOUDFRONT_COMMENT:
                    print(f"✓ CloudFront distribution already exists: {dist['DomainName']}")
                    print(f"  Distribution ID: {dist['Id']}")
                    return dist['DomainName'], dist['Id']
        
        # Create Origin Access Identity (OAI)
        print("Creating Origin Access Identity...")
        oai_response = cloudfront_client.create_cloud_front_origin_access_identity(
            CloudFrontOriginAccessIdentityConfig={
                'CallerReference': f"gramsetu-oai-{int(time.time())}",
                'Comment': 'OAI for GramSetu Web UI'
            }
        )
        
        oai_id = oai_response['CloudFrontOriginAccessIdentity']['Id']
        oai_canonical_user_id = oai_response['CloudFrontOriginAccessIdentity']['S3CanonicalUserId']
        print(f"✓ Created OAI: {oai_id}")
        
        # Get existing bucket policy (if any)
        try:
            existing_policy = s3_client.get_bucket_policy(Bucket=bucket_name)
            policy_doc = json.loads(existing_policy['Policy'])
            print(f"✓ Found existing bucket policy")
        except:
            policy_doc = {
                'Version': '2012-10-17',
                'Statement': []
            }
            print(f"✓ Creating new bucket policy")
        
        # Add CloudFront OAI statement (if not already present)
        oai_statement = {
            'Sid': 'CloudFrontOAIAccessWebUI',
            'Effect': 'Allow',
            'Principal': {
                'CanonicalUser': oai_canonical_user_id
            },
            'Action': 's3:GetObject',
            'Resource': f'arn:aws:s3:::{bucket_name}/{prefix}*'
        }
        
        # Remove old OAI statement if exists
        policy_doc['Statement'] = [s for s in policy_doc['Statement'] if s.get('Sid') != 'CloudFrontOAIAccessWebUI']
        policy_doc['Statement'].append(oai_statement)
        
        # Update bucket policy
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(policy_doc)
        )
        print(f"✓ Updated S3 bucket policy for CloudFront access")
        
        # S3 origin domain (not website endpoint)
        origin_domain = f"{bucket_name}.s3.{region}.amazonaws.com"
        origin_path = f"/{prefix.rstrip('/')}" if prefix else ""
        
        # Create new distribution
        caller_reference = f"gramsetu-{int(time.time())}"
        
        distribution_config = {
            'CallerReference': caller_reference,
            'Comment': CLOUDFRONT_COMMENT,
            'Enabled': True,
            'DefaultRootObject': 'index.html',
            'Origins': {
                'Quantity': 1,
                'Items': [{
                    'Id': 'S3-Origin',
                    'DomainName': origin_domain,
                    'OriginPath': origin_path,
                    'S3OriginConfig': {
                        'OriginAccessIdentity': f'origin-access-identity/cloudfront/{oai_id}'
                    }
                }]
            },
            'DefaultCacheBehavior': {
                'TargetOriginId': 'S3-Origin',
                'ViewerProtocolPolicy': 'redirect-to-https',
                'AllowedMethods': {
                    'Quantity': 2,
                    'Items': ['GET', 'HEAD'],
                    'CachedMethods': {
                        'Quantity': 2,
                        'Items': ['GET', 'HEAD']
                    }
                },
                'ForwardedValues': {
                    'QueryString': False,
                    'Cookies': {'Forward': 'none'}
                },
                'MinTTL': 0,
                'DefaultTTL': 300,
                'MaxTTL': 86400,
                'Compress': True
            },
            'CustomErrorResponses': {
                'Quantity': 1,
                'Items': [{
                    'ErrorCode': 404,
                    'ResponsePagePath': '/index.html',
                    'ResponseCode': '200',
                    'ErrorCachingMinTTL': 300
                }]
            },
            'PriceClass': 'PriceClass_100',  # Use only North America and Europe
            'ViewerCertificate': {
                'CloudFrontDefaultCertificate': True
            }
        }
        
        response = cloudfront_client.create_distribution(
            DistributionConfig=distribution_config
        )
        
        distribution = response['Distribution']
        domain_name = distribution['DomainName']
        distribution_id = distribution['Id']
        
        print(f"✓ CloudFront distribution created successfully")
        print(f"  Domain: {domain_name}")
        print(f"  Distribution ID: {distribution_id}")
        print(f"  Status: {distribution['Status']}")
        print(f"\n⏳ Distribution is being deployed (this may take 10-15 minutes)...")
        
        return domain_name, distribution_id
        
    except Exception as e:
        print(f"✗ Failed to create CloudFront distribution: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def update_config_file(api_gateway_url):
    """Update config.js with API Gateway URL"""
    config_file = Path(WEB_UI_DIR) / 'config.js'
    
    if not config_file.exists():
        print(f"✗ Config file not found: {config_file}")
        return False
    
    try:
        # Read current config
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Replace API Gateway URL
        content = content.replace(
            "window.API_GATEWAY_URL = 'YOUR_API_GATEWAY_URL_HERE';",
            f"window.API_GATEWAY_URL = '{api_gateway_url}';"
        )
        
        # Write updated config
        with open(config_file, 'w') as f:
            f.write(content)
        
        print(f"✓ Updated config.js with API Gateway URL")
        return True
        
    except Exception as e:
        print(f"✗ Failed to update config file: {e}")
        return False


def main():
    """Main deployment function"""
    print("=" * 60)
    print("GramSetu Web UI Deployment to AWS S3 + CloudFront")
    print("=" * 60)
    
    # Get API Gateway URL from CloudFormation stack
    print("\n1. Getting API Gateway URL from CloudFormation...")
    try:
        cfn_client = boto3.client('cloudformation')
        response = cfn_client.describe_stacks(StackName='ure-mvp-stack')
        
        api_url = None
        for output in response['Stacks'][0].get('Outputs', []):
            if output['OutputKey'] == 'ApiEndpoint':
                api_url = output['OutputValue']
                break
        
        if api_url:
            print(f"✓ API Gateway URL: {api_url}")
            
            # Update config file
            update_config_file(api_url)
        else:
            print("⚠ API Gateway URL not found in CloudFormation outputs")
            print("  You'll need to update config.js manually")
    
    except Exception as e:
        print(f"⚠ Could not get API Gateway URL: {e}")
        print("  You'll need to update config.js manually")
    
    # Create S3 bucket
    print("\n2. Checking S3 bucket...")
    if not create_s3_bucket(S3_BUCKET_NAME):
        print("⚠ Using existing bucket (this is OK)")
    
    # Upload files
    print("\n3. Uploading web UI files to S3...")
    if not upload_files_to_s3(S3_BUCKET_NAME, WEB_UI_DIR, WEB_UI_PREFIX):
        return
    
    # Create CloudFront distribution
    print("\n4. Creating CloudFront distribution...")
    domain_name, distribution_id = create_cloudfront_distribution(S3_BUCKET_NAME, WEB_UI_PREFIX)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Deployment Summary")
    print("=" * 60)
    print(f"S3 Bucket: {S3_BUCKET_NAME}")
    print(f"Web UI Path: s3://{S3_BUCKET_NAME}/{WEB_UI_PREFIX}")
    
    if domain_name:
        print(f"CloudFront URL: https://{domain_name}")
        print(f"Distribution ID: {distribution_id}")
        print("\n⏳ CloudFront distribution is being deployed...")
        print("   This may take 10-15 minutes to complete.")
        print(f"\n✓ Once deployed, access your app at: https://{domain_name}")
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("1. Wait for CloudFront distribution to deploy (10-15 minutes)")
    print("2. Update config.js with your API Gateway URL if not done automatically")
    print("3. Test the web UI by opening the CloudFront URL in your browser")
    print("4. Configure custom domain (optional)")
    print("\n✓ Deployment complete!")


if __name__ == "__main__":
    main()
