#!/usr/bin/env python3
"""
Privacy Auditor - PII Detection and Scanning
Scans stored data for Personally Identifiable Information (PII)
"""

import re
import json
import logging
from typing import Dict, List, Any, Set
from datetime import datetime

logger = logging.getLogger(__name__)


class PIIDetector:
    """Detects various types of PII in text data"""
    
    # Regex patterns for common PII types
    PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone_indian': r'\b(?:\+91|0)?[6-9]\d{9}\b',
        'phone_international': r'\b\+\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b',
        'aadhaar': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        'pan': r'\b[A-Z]{5}\d{4}[A-Z]\b',
        'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        'url': r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)',
        'postal_code_indian': r'\b\d{6}\b',
        'coordinates': r'\b-?\d{1,3}\.\d{4,},\s*-?\d{1,3}\.\d{4,}\b',
    }
    
    # Common Indian name patterns (basic detection)
    NAME_INDICATORS = [
        r'\bMr\.?\s+[A-Z][a-z]+',
        r'\bMrs\.?\s+[A-Z][a-z]+',
        r'\bMs\.?\s+[A-Z][a-z]+',
        r'\bDr\.?\s+[A-Z][a-z]+',
        r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # Full names
    ]
    
    # Address indicators
    ADDRESS_KEYWORDS = [
        'address', 'street', 'road', 'lane', 'colony', 'nagar',
        'village', 'taluka', 'tehsil', 'pin code', 'pincode'
    ]
    
    def __init__(self):
        """Initialize PII detector with compiled patterns"""
        self.compiled_patterns = {
            name: re.compile(pattern, re.IGNORECASE)
            for name, pattern in self.PATTERNS.items()
        }
        self.name_patterns = [
            re.compile(pattern) for pattern in self.NAME_INDICATORS
        ]
    
    def detect_pii(self, text: str) -> Dict[str, List[str]]:
        """
        Detect PII in text
        
        Args:
            text: Text to scan for PII
        
        Returns:
            dict: Dictionary of PII types found with their values
        """
        if not text or not isinstance(text, str):
            return {}
        
        findings = {}
        
        # Check each pattern
        for pii_type, pattern in self.compiled_patterns.items():
            matches = pattern.findall(text)
            if matches:
                # Deduplicate matches
                unique_matches = list(set(matches))
                findings[pii_type] = unique_matches
        
        # Check for names
        name_matches = []
        for pattern in self.name_patterns:
            matches = pattern.findall(text)
            name_matches.extend(matches)
        
        if name_matches:
            findings['potential_names'] = list(set(name_matches))
        
        # Check for address indicators
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in self.ADDRESS_KEYWORDS):
            findings['potential_address'] = ['Address keywords detected']
        
        return findings
    
    def scan_dict(self, data: Dict[str, Any], path: str = "") -> List[Dict[str, Any]]:
        """
        Recursively scan dictionary for PII
        
        Args:
            data: Dictionary to scan
            path: Current path in the data structure
        
        Returns:
            list: List of PII findings with locations
        """
        findings = []
        
        if not isinstance(data, dict):
            return findings
        
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            
            if isinstance(value, str):
                # Scan string value
                pii_found = self.detect_pii(value)
                if pii_found:
                    findings.append({
                        'location': current_path,
                        'pii_types': list(pii_found.keys()),
                        'details': pii_found
                    })
            
            elif isinstance(value, dict):
                # Recursively scan nested dict
                findings.extend(self.scan_dict(value, current_path))
            
            elif isinstance(value, list):
                # Scan list items
                for idx, item in enumerate(value):
                    if isinstance(item, str):
                        pii_found = self.detect_pii(item)
                        if pii_found:
                            findings.append({
                                'location': f"{current_path}[{idx}]",
                                'pii_types': list(pii_found.keys()),
                                'details': pii_found
                            })
                    elif isinstance(item, dict):
                        findings.extend(self.scan_dict(item, f"{current_path}[{idx}]"))
        
        return findings


class PrivacyAuditor:
    """Audits stored data for privacy compliance"""
    
    def __init__(self):
        """Initialize privacy auditor"""
        self.detector = PIIDetector()
    
    def audit_conversation(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Audit a single conversation for PII
        
        Args:
            conversation: Conversation data to audit
        
        Returns:
            dict: Audit results
        """
        findings = self.detector.scan_dict(conversation)
        
        return {
            'has_pii': len(findings) > 0,
            'pii_count': len(findings),
            'findings': findings,
            'timestamp': conversation.get('timestamp', 'unknown')
        }
    
    def audit_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Audit all user data for PII
        
        Args:
            user_data: Complete user data including conversations and profile
        
        Returns:
            dict: Comprehensive audit report
        """
        report = {
            'audit_timestamp': datetime.utcnow().isoformat(),
            'user_id': user_data.get('user_id', 'unknown'),
            'total_pii_findings': 0,
            'conversations_with_pii': 0,
            'profile_has_pii': False,
            'pii_types_found': set(),
            'findings': [],
            'recommendations': []
        }
        
        # Audit conversations
        conversations = user_data.get('conversations', [])
        for idx, conv in enumerate(conversations):
            audit_result = self.audit_conversation(conv)
            if audit_result['has_pii']:
                report['conversations_with_pii'] += 1
                report['total_pii_findings'] += audit_result['pii_count']
                
                # Collect PII types
                for finding in audit_result['findings']:
                    report['pii_types_found'].update(finding['pii_types'])
                
                report['findings'].append({
                    'type': 'conversation',
                    'index': idx,
                    'timestamp': audit_result['timestamp'],
                    'pii_count': audit_result['pii_count'],
                    'details': audit_result['findings']
                })
        
        # Audit user profile (excluding user_id which is expected)
        profile_data = {k: v for k, v in user_data.items() 
                       if k not in ['user_id', 'conversations', 'expiry_time', 'last_updated']}
        
        if profile_data:
            profile_findings = self.detector.scan_dict(profile_data)
            if profile_findings:
                report['profile_has_pii'] = True
                report['total_pii_findings'] += len(profile_findings)
                
                for finding in profile_findings:
                    report['pii_types_found'].update(finding['pii_types'])
                
                report['findings'].append({
                    'type': 'profile',
                    'details': profile_findings
                })
        
        # Convert set to list for JSON serialization
        report['pii_types_found'] = list(report['pii_types_found'])
        
        # Generate recommendations
        report['recommendations'] = self._generate_recommendations(report)
        
        return report
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate privacy recommendations based on audit findings"""
        recommendations = []
        
        pii_types = report['pii_types_found']
        
        if 'email' in pii_types:
            recommendations.append("Email addresses detected. Consider hashing or removing emails from stored conversations.")
        
        if 'phone_indian' in pii_types or 'phone_international' in pii_types:
            recommendations.append("Phone numbers detected. Consider redacting phone numbers before storage.")
        
        if 'aadhaar' in pii_types:
            recommendations.append("CRITICAL: Aadhaar numbers detected. This is sensitive PII and should be immediately redacted.")
        
        if 'pan' in pii_types:
            recommendations.append("PAN card numbers detected. Consider redacting PAN numbers from conversations.")
        
        if 'credit_card' in pii_types:
            recommendations.append("CRITICAL: Credit card numbers detected. This should never be stored and must be redacted immediately.")
        
        if 'ip_address' in pii_types:
            recommendations.append("IP addresses detected in plaintext. Ensure IP addresses are hashed before storage.")
        
        if 'potential_names' in pii_types:
            recommendations.append("Potential names detected. Review if name storage is necessary for the use case.")
        
        if 'potential_address' in pii_types:
            recommendations.append("Address information detected. Consider storing only district/state level location data.")
        
        if report['total_pii_findings'] == 0:
            recommendations.append("No PII detected. Good privacy practices!")
        
        if report['conversations_with_pii'] > 0:
            percentage = (report['conversations_with_pii'] / len(report.get('findings', [1]))) * 100
            recommendations.append(f"{percentage:.1f}% of conversations contain PII. Consider implementing PII redaction.")
        
        return recommendations
    
    def generate_summary_report(self, audit_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary report from multiple user audits
        
        Args:
            audit_results: List of individual user audit results
        
        Returns:
            dict: Summary report
        """
        summary = {
            'audit_timestamp': datetime.utcnow().isoformat(),
            'total_users_audited': len(audit_results),
            'users_with_pii': 0,
            'total_pii_findings': 0,
            'pii_types_distribution': {},
            'high_risk_users': [],
            'recommendations': []
        }
        
        all_pii_types = set()
        
        for result in audit_results:
            if result['total_pii_findings'] > 0:
                summary['users_with_pii'] += 1
                summary['total_pii_findings'] += result['total_pii_findings']
                
                # Track PII types
                for pii_type in result['pii_types_found']:
                    all_pii_types.add(pii_type)
                    summary['pii_types_distribution'][pii_type] = \
                        summary['pii_types_distribution'].get(pii_type, 0) + 1
                
                # Flag high-risk users (with sensitive PII)
                sensitive_pii = {'aadhaar', 'pan', 'credit_card'}
                if any(pii in result['pii_types_found'] for pii in sensitive_pii):
                    summary['high_risk_users'].append({
                        'user_id': result['user_id'],
                        'pii_count': result['total_pii_findings'],
                        'sensitive_types': [t for t in result['pii_types_found'] if t in sensitive_pii]
                    })
        
        # Generate summary recommendations
        if summary['users_with_pii'] > 0:
            percentage = (summary['users_with_pii'] / summary['total_users_audited']) * 100
            summary['recommendations'].append(
                f"{percentage:.1f}% of users have PII in their data. Implement PII redaction pipeline."
            )
        
        if summary['high_risk_users']:
            summary['recommendations'].append(
                f"CRITICAL: {len(summary['high_risk_users'])} users have sensitive PII (Aadhaar/PAN/Credit Card). Immediate action required."
            )
        
        if 'ip_address' in all_pii_types:
            summary['recommendations'].append(
                "Plaintext IP addresses detected. Verify IP hashing is working correctly."
            )
        
        return summary


def audit_sample_data(sample_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to audit sample data
    
    Args:
        sample_data: Sample user data to audit
    
    Returns:
        dict: Audit report
    """
    auditor = PrivacyAuditor()
    return auditor.audit_user_data(sample_data)


# Singleton instance
_auditor_instance = None

def get_privacy_auditor() -> PrivacyAuditor:
    """Get or create singleton privacy auditor instance"""
    global _auditor_instance
    if _auditor_instance is None:
        _auditor_instance = PrivacyAuditor()
    return _auditor_instance
