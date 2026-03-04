#!/usr/bin/env python3
"""
AWS Services Management Script
Check status, enable, and disable AWS services used by GramSetu
"""

import boto3
import json
from datetime import datetime
from botocore.exceptions import ClientError

# AWS Configuration
REGION = 'us-east-1'
ACCOUNT_ID = '188238313375'

# Service configurations
SERVICES = {
    'lambda': {
        'name': 'AWS Lambda',
        'function_name': 'ure-mvp-handler',
        'description': 'Main application handler'
    },
    'api_gateway': {
        'name': 'API Gateway',
        'api_id': '8938dqxf33',
        'stage': 'dev',
        'description': 'REST API endpoint'
    },
    'cloudfront': {
        'name': 'CloudFront CDN',
        'distribution_id': 'E354ZTACSUHKWS',
        'description': 'Web UI delivery'
    },
    's3': {
        'name': 'S3 Storage',
        'bucket_name': 'ure-mvp-data-us-east-1-188238313375',
        'description': 'Data storage'
    },
    'dynamodb': {
        'name': 'DynamoDB',
        'tables': ['ure-conversations', 'ure-user-profiles', 'ure-village-amenities'],
        'description': 'Database tables'
    },
    'bedrock': {
        'name': 'Amazon Bedrock',
        'model_id': 'amazon.nova-lite-v1:0',
        'description': 'AI model'
    }
}

class AWSServiceManager:
    def __init__(self):
        self.lambda_client = boto3.client('lambda', region_name=REGION)
        self.apigateway_client = boto3.client('apigateway', region_name=REGION)
        self.cloudfront_client = boto3.client('cloudfront')
        self.s3_client = boto3.client('s3', region_name=REGION)
        self.dynamodb_client = boto3.client('dynamodb', region_name=REGION)
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=REGION)
    
    def check_lambda_status(self):
        """Check Lambda function status"""
        try:
            response = self.lambda_client.get_function(
                FunctionName=SERVICES['lambda']['function_name']
            )
            
            config = response['Configuration']
            return {
                'status': 'Active' if config['State'] == 'Active' else config['State'],
                'last_modified': config['LastModified'],
                'runtime': config['Runtime'],
                'memory': f"{config['MemorySize']} MB",
                'timeout': f"{config['Timeout']} seconds",
                'version': config['Version'],
                'enabled': True
            }
        except ClientError as e:
            return {'status': 'Error', 'error': str(e), 'enabled': False}

    def check_api_gateway_status(self):
        """Check API Gateway status"""
        try:
            response = self.apigateway_client.get_rest_api(
                restApiId=SERVICES['api_gateway']['api_id']
            )
            
            # Get stage info
            stage_response = self.apigateway_client.get_stage(
                restApiId=SERVICES['api_gateway']['api_id'],
                stageName=SERVICES['api_gateway']['stage']
            )
            
            return {
                'status': 'Active',
                'api_name': response['name'],
                'endpoint': f"https://{SERVICES['api_gateway']['api_id']}.execute-api.{REGION}.amazonaws.com/{SERVICES['api_gateway']['stage']}",
                'stage': SERVICES['api_gateway']['stage'],
                'created': response.get('createdDate', 'N/A'),
                'enabled': True
            }
        except ClientError as e:
            return {'status': 'Error', 'error': str(e), 'enabled': False}
    
    def check_cloudfront_status(self):
        """Check CloudFront distribution status"""
        try:
            response = self.cloudfront_client.get_distribution(
                Id=SERVICES['cloudfront']['distribution_id']
            )
            
            dist = response['Distribution']
            config = dist['DistributionConfig']
            
            return {
                'status': dist['Status'],
                'domain': dist['DomainName'],
                'enabled': config['Enabled'],
                'price_class': config['PriceClass'],
                'last_modified': dist['LastModifiedTime'].strftime('%Y-%m-%d %H:%M:%S')
            }
        except ClientError as e:
            return {'status': 'Error', 'error': str(e), 'enabled': False}
    
    def check_s3_status(self):
        """Check S3 bucket status"""
        try:
            # Check if bucket exists
            self.s3_client.head_bucket(Bucket=SERVICES['s3']['bucket_name'])
            
            # Get bucket size
            response = self.s3_client.list_objects_v2(
                Bucket=SERVICES['s3']['bucket_name']
            )
            
            total_size = 0
            file_count = 0
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    total_size += obj['Size']
                    file_count += 1
            
            return {
                'status': 'Active',
                'bucket_name': SERVICES['s3']['bucket_name'],
                'file_count': file_count,
                'total_size': f"{total_size / (1024**3):.2f} GB",
                'enabled': True
            }
        except ClientError as e:
            return {'status': 'Error', 'error': str(e), 'enabled': False}
    
    def check_dynamodb_status(self):
        """Check DynamoDB tables status"""
        tables_status = {}
        
        for table_name in SERVICES['dynamodb']['tables']:
            try:
                response = self.dynamodb_client.describe_table(
                    TableName=table_name
                )
                
                table = response['Table']
                tables_status[table_name] = {
                    'status': table['TableStatus'],
                    'item_count': table['ItemCount'],
                    'size': f"{table['TableSizeBytes'] / 1024:.2f} KB",
                    'created': table['CreationDateTime'].strftime('%Y-%m-%d %H:%M:%S'),
                    'enabled': True
                }
            except ClientError as e:
                tables_status[table_name] = {
                    'status': 'Error',
                    'error': str(e),
                    'enabled': False
                }
        
        return tables_status
    
    def check_bedrock_status(self):
        """Check Bedrock model access"""
        try:
            # Try to invoke model with a simple test
            response = self.bedrock_client.converse(
                modelId=SERVICES['bedrock']['model_id'],
                messages=[{
                    "role": "user",
                    "content": [{"text": "test"}]
                }],
                inferenceConfig={
                    "maxTokens": 10,
                    "temperature": 0.1
                }
            )
            
            return {
                'status': 'Active',
                'model_id': SERVICES['bedrock']['model_id'],
                'access': 'Granted',
                'enabled': True
            }
        except ClientError as e:
            return {
                'status': 'Error',
                'error': str(e),
                'enabled': False
            }
    
    def disable_lambda(self):
        """Disable Lambda function by setting reserved concurrency to 0"""
        try:
            self.lambda_client.put_function_concurrency(
                FunctionName=SERVICES['lambda']['function_name'],
                ReservedConcurrentExecutions=0
            )
            return {'success': True, 'message': 'Lambda function disabled'}
        except ClientError as e:
            return {'success': False, 'error': str(e)}
    
    def enable_lambda(self):
        """Enable Lambda function by removing concurrency limit"""
        try:
            self.lambda_client.delete_function_concurrency(
                FunctionName=SERVICES['lambda']['function_name']
            )
            return {'success': True, 'message': 'Lambda function enabled'}
        except ClientError as e:
            return {'success': False, 'error': str(e)}
    
    def disable_cloudfront(self):
        """Disable CloudFront distribution"""
        try:
            # Get current config
            response = self.cloudfront_client.get_distribution_config(
                Id=SERVICES['cloudfront']['distribution_id']
            )
            
            config = response['DistributionConfig']
            etag = response['ETag']
            
            # Disable distribution
            config['Enabled'] = False
            
            self.cloudfront_client.update_distribution(
                Id=SERVICES['cloudfront']['distribution_id'],
                DistributionConfig=config,
                IfMatch=etag
            )
            
            return {'success': True, 'message': 'CloudFront distribution disabled (will take 15-20 minutes)'}
        except ClientError as e:
            return {'success': False, 'error': str(e)}
    
    def enable_cloudfront(self):
        """Enable CloudFront distribution"""
        try:
            # Get current config
            response = self.cloudfront_client.get_distribution_config(
                Id=SERVICES['cloudfront']['distribution_id']
            )
            
            config = response['DistributionConfig']
            etag = response['ETag']
            
            # Enable distribution
            config['Enabled'] = True
            
            self.cloudfront_client.update_distribution(
                Id=SERVICES['cloudfront']['distribution_id'],
                DistributionConfig=config,
                IfMatch=etag
            )
            
            return {'success': True, 'message': 'CloudFront distribution enabled (will take 15-20 minutes)'}
        except ClientError as e:
            return {'success': False, 'error': str(e)}
    
    def disable_all_services(self):
        """Disable all controllable services"""
        results = {}
        
        print("\n⚠️ Disabling all services...")
        
        # Disable Lambda
        print("  → Disabling Lambda...")
        results['lambda'] = self.disable_lambda()
        
        # Disable CloudFront
        print("  → Disabling CloudFront...")
        results['cloudfront'] = self.disable_cloudfront()
        
        return results
    
    def enable_all_services(self):
        """Enable all controllable services"""
        results = {}
        
        print("\n✓ Enabling all services...")
        
        # Enable Lambda
        print("  → Enabling Lambda...")
        results['lambda'] = self.enable_lambda()
        
        # Enable CloudFront
        print("  → Enabling CloudFront...")
        results['cloudfront'] = self.enable_cloudfront()
        
        return results


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_service_status(service_name, status_data):
    """Print service status in formatted way"""
    print(f"\n📊 {service_name}")
    print("-" * 70)
    
    for key, value in status_data.items():
        if key != 'enabled':
            print(f"  {key.replace('_', ' ').title()}: {value}")


def main():
    print_header("GramSetu AWS Services Manager")
    print(f"Account: {ACCOUNT_ID}")
    print(f"Region: {REGION}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    manager = AWSServiceManager()
    
    # Check all services
    print_header("Service Status Check")
    
    print("\n🔧 Checking Lambda Function...")
    lambda_status = manager.check_lambda_status()
    print_service_status("AWS Lambda", lambda_status)
    
    print("\n🌐 Checking API Gateway...")
    api_status = manager.check_api_gateway_status()
    print_service_status("API Gateway", api_status)
    
    print("\n☁️ Checking CloudFront CDN...")
    cloudfront_status = manager.check_cloudfront_status()
    print_service_status("CloudFront", cloudfront_status)
    
    print("\n📦 Checking S3 Bucket...")
    s3_status = manager.check_s3_status()
    print_service_status("S3 Storage", s3_status)
    
    print("\n🗄️ Checking DynamoDB Tables...")
    dynamodb_status = manager.check_dynamodb_status()
    for table_name, status in dynamodb_status.items():
        print_service_status(f"DynamoDB - {table_name}", status)
    
    print("\n🤖 Checking Bedrock AI Model...")
    bedrock_status = manager.check_bedrock_status()
    print_service_status("Amazon Bedrock", bedrock_status)
    
    # Summary
    print_header("Summary")
    
    all_services = {
        'Lambda': lambda_status.get('enabled', False),
        'API Gateway': api_status.get('enabled', False),
        'CloudFront': cloudfront_status.get('enabled', False),
        'S3': s3_status.get('enabled', False),
        'Bedrock': bedrock_status.get('enabled', False)
    }
    
    for table_name, status in dynamodb_status.items():
        all_services[f'DynamoDB-{table_name}'] = status.get('enabled', False)
    
    enabled_count = sum(1 for enabled in all_services.values() if enabled)
    total_count = len(all_services)
    
    print(f"\n✅ Enabled Services: {enabled_count}/{total_count}")
    print(f"❌ Disabled Services: {total_count - enabled_count}/{total_count}")
    
    print("\n" + "="*70)
    
    # Interactive menu
    print("\n📋 Management Options:")
    print("  1. Disable Lambda Function")
    print("  2. Enable Lambda Function")
    print("  3. Disable CloudFront CDN")
    print("  4. Enable CloudFront CDN")
    print("  5. 🔴 DISABLE ALL SERVICES")
    print("  6. 🟢 ENABLE ALL SERVICES")
    print("  7. Exit")
    
    choice = input("\nEnter your choice (1-7): ").strip()
    
    if choice == '1':
        print("\n⚠️ Disabling Lambda function...")
        result = manager.disable_lambda()
        print(f"{'✓' if result['success'] else '✗'} {result.get('message', result.get('error'))}")
    
    elif choice == '2':
        print("\n✓ Enabling Lambda function...")
        result = manager.enable_lambda()
        print(f"{'✓' if result['success'] else '✗'} {result.get('message', result.get('error'))}")
    
    elif choice == '3':
        confirm = input("\n⚠️ This will disable your web application. Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            print("\n⚠️ Disabling CloudFront distribution...")
            result = manager.disable_cloudfront()
            print(f"{'✓' if result['success'] else '✗'} {result.get('message', result.get('error'))}")
    
    elif choice == '4':
        print("\n✓ Enabling CloudFront distribution...")
        result = manager.enable_cloudfront()
        print(f"{'✓' if result['success'] else '✗'} {result.get('message', result.get('error'))}")
    
    elif choice == '5':
        confirm = input("\n🔴 WARNING: This will DISABLE ALL SERVICES and take down your application. Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            results = manager.disable_all_services()
            print("\n📊 Results:")
            for service, result in results.items():
                status = '✓' if result['success'] else '✗'
                message = result.get('message', result.get('error'))
                print(f"  {status} {service.title()}: {message}")
            print("\n⚠️ All services disabled. Your application is now offline.")
        else:
            print("\n❌ Operation cancelled")
    
    elif choice == '6':
        confirm = input("\n🟢 This will ENABLE ALL SERVICES and bring your application online. Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            results = manager.enable_all_services()
            print("\n📊 Results:")
            for service, result in results.items():
                status = '✓' if result['success'] else '✗'
                message = result.get('message', result.get('error'))
                print(f"  {status} {service.title()}: {message}")
            print("\n✓ All services enabled. Your application will be online shortly.")
        else:
            print("\n❌ Operation cancelled")
    
    elif choice == '7':
        print("\n👋 Goodbye!")
    
    else:
        print("\n❌ Invalid choice")


if __name__ == "__main__":
    main()
