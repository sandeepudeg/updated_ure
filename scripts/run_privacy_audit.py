#!/usr/bin/env python3
"""
Privacy Audit Script
Scans DynamoDB tables for PII and generates audit reports
"""

import sys
import os
import json
import boto3
from datetime import datetime
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.privacy_auditor import PrivacyAuditor

# AWS Configuration
CONVERSATIONS_TABLE = os.environ.get('DYNAMODB_TABLE_NAME', 'ure-conversations')
USER_TABLE = os.environ.get('DYNAMODB_USER_TABLE', 'ure-user-profiles')
REGION = os.environ.get('AWS_REGION', 'us-east-1')


def scan_conversations_table(limit: int = None) -> List[Dict[str, Any]]:
    """
    Scan conversations table
    
    Args:
        limit: Maximum number of items to scan (None for all)
    
    Returns:
        list: List of conversation items
    """
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    table = dynamodb.Table(CONVERSATIONS_TABLE)
    
    items = []
    scan_kwargs = {}
    
    if limit:
        scan_kwargs['Limit'] = limit
    
    try:
        response = table.scan(**scan_kwargs)
        items.extend(response.get('Items', []))
        
        # Handle pagination
        while 'LastEvaluatedKey' in response and (not limit or len(items) < limit):
            scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
            if limit:
                scan_kwargs['Limit'] = limit - len(items)
            
            response = table.scan(**scan_kwargs)
            items.extend(response.get('Items', []))
        
        print(f"✓ Scanned {len(items)} items from {CONVERSATIONS_TABLE}")
        return items
    
    except Exception as e:
        print(f"✗ Error scanning {CONVERSATIONS_TABLE}: {e}")
        return []


def audit_all_users(limit: int = None) -> Dict[str, Any]:
    """
    Audit all users for PII
    
    Args:
        limit: Maximum number of users to audit
    
    Returns:
        dict: Audit summary report
    """
    print("\n" + "="*60)
    print("PRIVACY AUDIT - PII Detection")
    print("="*60)
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print(f"Region: {REGION}")
    print(f"Table: {CONVERSATIONS_TABLE}")
    print("="*60 + "\n")
    
    # Scan conversations table
    print("📊 Scanning DynamoDB table...")
    user_data_items = scan_conversations_table(limit)
    
    if not user_data_items:
        print("\n⚠️  No data found to audit")
        return {
            'status': 'no_data',
            'message': 'No data found in conversations table'
        }
    
    # Initialize auditor
    auditor = PrivacyAuditor()
    
    # Audit each user
    print(f"\n🔍 Auditing {len(user_data_items)} users for PII...\n")
    audit_results = []
    
    for idx, user_data in enumerate(user_data_items, 1):
        user_id = user_data.get('user_id', 'unknown')
        print(f"  [{idx}/{len(user_data_items)}] Auditing user: {user_id[:20]}...")
        
        audit_result = auditor.audit_user_data(user_data)
        audit_results.append(audit_result)
        
        # Print immediate findings
        if audit_result['total_pii_findings'] > 0:
            print(f"      ⚠️  Found {audit_result['total_pii_findings']} PII instances")
            print(f"      Types: {', '.join(audit_result['pii_types_found'])}")
    
    # Generate summary report
    print("\n📋 Generating summary report...")
    summary = auditor.generate_summary_report(audit_results)
    
    return {
        'status': 'completed',
        'summary': summary,
        'detailed_results': audit_results
    }


def print_summary_report(report: Dict[str, Any]):
    """Print formatted summary report"""
    if report['status'] != 'completed':
        print(f"\n{report.get('message', 'Audit incomplete')}")
        return
    
    summary = report['summary']
    
    print("\n" + "="*60)
    print("AUDIT SUMMARY")
    print("="*60)
    
    print(f"\n📊 Statistics:")
    print(f"  Total users audited: {summary['total_users_audited']}")
    print(f"  Users with PII: {summary['users_with_pii']}")
    print(f"  Total PII findings: {summary['total_pii_findings']}")
    
    if summary['pii_types_distribution']:
        print(f"\n🔍 PII Types Found:")
        for pii_type, count in sorted(summary['pii_types_distribution'].items(), 
                                      key=lambda x: x[1], reverse=True):
            print(f"  - {pii_type}: {count} occurrences")
    
    if summary['high_risk_users']:
        print(f"\n⚠️  HIGH RISK USERS ({len(summary['high_risk_users'])}):")
        for user in summary['high_risk_users'][:5]:  # Show first 5
            print(f"  - {user['user_id'][:20]}: {user['sensitive_types']}")
        if len(summary['high_risk_users']) > 5:
            print(f"  ... and {len(summary['high_risk_users']) - 5} more")
    
    if summary['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in summary['recommendations']:
            print(f"  • {rec}")
    
    print("\n" + "="*60)


def save_detailed_report(report: Dict[str, Any], output_file: str = None):
    """Save detailed report to JSON file"""
    if output_file is None:
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        output_file = f"privacy_audit_report_{timestamp}.json"
    
    try:
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n💾 Detailed report saved to: {output_file}")
    except Exception as e:
        print(f"\n✗ Failed to save report: {e}")


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run privacy audit on DynamoDB data')
    parser.add_argument('--limit', type=int, help='Limit number of users to audit')
    parser.add_argument('--output', type=str, help='Output file for detailed report')
    parser.add_argument('--no-save', action='store_true', help='Do not save detailed report')
    
    args = parser.parse_args()
    
    try:
        # Run audit
        report = audit_all_users(limit=args.limit)
        
        # Print summary
        print_summary_report(report)
        
        # Save detailed report
        if not args.no_save and report['status'] == 'completed':
            save_detailed_report(report, args.output)
        
        # Exit with appropriate code
        if report['status'] == 'completed':
            summary = report['summary']
            if summary['high_risk_users']:
                print("\n⚠️  WARNING: High-risk PII detected. Immediate action required!")
                sys.exit(2)
            elif summary['users_with_pii'] > 0:
                print("\n⚠️  PII detected. Review recommendations.")
                sys.exit(1)
            else:
                print("\n✓ No PII detected. Privacy compliance looks good!")
                sys.exit(0)
        else:
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Audit interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n✗ Audit failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
