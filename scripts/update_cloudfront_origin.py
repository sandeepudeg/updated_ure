#!/usr/bin/env python3
"""
Update CloudFront Distribution Origin to Use Data Bucket
"""

import boto3
import json

DISTRIBUTION_ID = "E354ZTACSUHKWS"
NEW_BUCKET = "ure-mvp-data-us-east-1-188238313375"
NEW_ORIGIN_PATH = "/web-ui"

def update_cloudfront_origin():
    """Update CloudFront distribution to use new S3 bucket and path"""
    cloudfront = boto3.client('cloudfront')
    
    print("=" * 60)
    print("Updating CloudFront Distribution Origin")
    print("=" * 60)
    
    try:
        # Get current distribution config
        print(f"\n1. Getting current distribution config...")
        response = cloudfront.get_distribution_config(Id=DISTRIBUTION_ID)
        config = response['DistributionConfig']
        etag = response['ETag']
        
        print(f"✓ Current distribution: {DISTRIBUTION_ID}")
        print(f"  Current origin: {config['Origins']['Items'][0]['DomainName']}")
        print(f"  Current path: {config['Origins']['Items'][0].get('OriginPath', '/')}")
        
        # Update origin
        print(f"\n2. Updating origin configuration...")
        new_origin_domain = f"{NEW_BUCKET}.s3.us-east-1.amazonaws.com"
        
        config['Origins']['Items'][0]['DomainName'] = new_origin_domain
        config['Origins']['Items'][0]['OriginPath'] = NEW_ORIGIN_PATH
        
        print(f"✓ New origin: {new_origin_domain}")
        print(f"✓ New path: {NEW_ORIGIN_PATH}")
        
        # Update distribution
        print(f"\n3. Applying changes to CloudFront...")
        update_response = cloudfront.update_distribution(
            Id=DISTRIBUTION_ID,
            DistributionConfig=config,
            IfMatch=etag
        )
        
        print(f"✓ Distribution updated successfully")
        print(f"  Status: {update_response['Distribution']['Status']}")
        print(f"  Domain: {update_response['Distribution']['DomainName']}")
        
        print(f"\n⏳ Changes are being deployed (5-10 minutes)...")
        print(f"   CloudFront URL: https://{update_response['Distribution']['DomainName']}")
        
        print("\n" + "=" * 60)
        print("Update Complete")
        print("=" * 60)
        print(f"\nYour web UI is now served from:")
        print(f"  S3: s3://{NEW_BUCKET}{NEW_ORIGIN_PATH}/")
        print(f"  CloudFront: https://{update_response['Distribution']['DomainName']}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Failed to update distribution: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    update_cloudfront_origin()
