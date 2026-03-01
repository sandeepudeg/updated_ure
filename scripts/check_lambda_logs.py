#!/usr/bin/env python3
"""
Check Lambda CloudWatch logs for errors
"""

import boto3
import time
from datetime import datetime, timedelta

REGION = 'ap-south-1'
FUNCTION_NAME = 'ure-mvp-handler-mumbai'
LOG_GROUP = f'/aws/lambda/{FUNCTION_NAME}'

def get_recent_logs(minutes=10):
    """Get recent Lambda logs"""
    logs_client = boto3.client('logs', region_name=REGION)
    
    print("=" * 60)
    print("LAMBDA CLOUDWATCH LOGS")
    print("=" * 60)
    print(f"Function: {FUNCTION_NAME}")
    print(f"Region: {REGION}")
    print(f"Last {minutes} minutes")
    print("=" * 60)
    print()
    
    try:
        # Calculate time range
        end_time = int(time.time() * 1000)
        start_time = int((time.time() - minutes * 60) * 1000)
        
        # Get log streams
        streams_response = logs_client.describe_log_streams(
            logGroupName=LOG_GROUP,
            orderBy='LastEventTime',
            descending=True,
            limit=5
        )
        
        if not streams_response.get('logStreams'):
            print("No log streams found")
            return
        
        print(f"Found {len(streams_response['logStreams'])} recent log streams")
        print()
        
        # Get logs from each stream
        for stream in streams_response['logStreams']:
            stream_name = stream['logStreamName']
            print(f"Stream: {stream_name}")
            print("-" * 60)
            
            try:
                events_response = logs_client.get_log_events(
                    logGroupName=LOG_GROUP,
                    logStreamName=stream_name,
                    startTime=start_time,
                    endTime=end_time,
                    limit=50
                )
                
                events = events_response.get('events', [])
                
                if not events:
                    print("  No events in time range")
                    print()
                    continue
                
                for event in events:
                    timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
                    message = event['message'].strip()
                    
                    # Highlight errors
                    if 'ERROR' in message or 'Error' in message or 'error' in message:
                        print(f"  ❌ [{timestamp}] {message}")
                    elif 'WARNING' in message or 'Warning' in message:
                        print(f"  ⚠️  [{timestamp}] {message}")
                    else:
                        print(f"  [{timestamp}] {message}")
                
                print()
                
            except Exception as e:
                print(f"  Error reading stream: {e}")
                print()
        
    except Exception as e:
        print(f"Error getting logs: {e}")


def check_lambda_status():
    """Check Lambda function status"""
    lambda_client = boto3.client('lambda', region_name=REGION)
    
    print("=" * 60)
    print("LAMBDA FUNCTION STATUS")
    print("=" * 60)
    print()
    
    try:
        response = lambda_client.get_function(FunctionName=FUNCTION_NAME)
        
        config = response['Configuration']
        
        print(f"Function Name: {config['FunctionName']}")
        print(f"Runtime: {config['Runtime']}")
        print(f"Handler: {config['Handler']}")
        print(f"State: {config['State']}")
        print(f"Last Modified: {config['LastModified']}")
        print(f"Memory: {config['MemorySize']} MB")
        print(f"Timeout: {config['Timeout']} seconds")
        print()
        
        # Check environment variables
        env_vars = config.get('Environment', {}).get('Variables', {})
        print("Environment Variables:")
        print(f"  BEDROCK_MODEL_ID: {env_vars.get('BEDROCK_MODEL_ID', 'Not set')}")
        print(f"  BEDROCK_REGION: {env_vars.get('BEDROCK_REGION', 'Not set')}")
        print()
        
        # Check if function is ready
        if config['State'] != 'Active':
            print(f"⚠️  Warning: Function state is {config['State']}, not Active")
            print()
        
        return True
        
    except Exception as e:
        print(f"Error getting function status: {e}")
        return False


def main():
    """Main execution"""
    print("\n" + "=" * 60)
    print("LAMBDA DIAGNOSTICS")
    print("=" * 60)
    print()
    
    # Check function status
    if not check_lambda_status():
        print("Could not get Lambda status. Exiting.")
        return
    
    # Get recent logs
    get_recent_logs(minutes=10)
    
    print("=" * 60)
    print("DIAGNOSTICS COMPLETE")
    print("=" * 60)
    print()
    print("If you see errors above:")
    print("  1. Check for Bedrock model access errors")
    print("  2. Check for IAM permission errors")
    print("  3. Check for timeout errors")
    print("  4. Run: py scripts/redeploy_mumbai_lambda.py")
    print()


if __name__ == "__main__":
    main()
