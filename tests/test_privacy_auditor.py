#!/usr/bin/env python3
"""
Unit tests for Privacy Auditor
Tests PII detection and privacy audit functionality
"""

import pytest
from src.utils.privacy_auditor import PIIDetector, PrivacyAuditor, audit_sample_data


class TestPIIDetector:
    """Test PII detection functionality"""
    
    def test_detect_email(self):
        """Test email detection"""
        detector = PIIDetector()
        text = "Contact me at farmer@example.com or support@agri.in"
        
        findings = detector.detect_pii(text)
        
        assert 'email' in findings
        assert len(findings['email']) == 2
        assert 'farmer@example.com' in findings['email']
        assert 'support@agri.in' in findings['email']
    
    def test_detect_indian_phone(self):
        """Test Indian phone number detection"""
        detector = PIIDetector()
        text = "Call me at 9876543210 or +919876543210"
        
        findings = detector.detect_pii(text)
        
        assert 'phone_indian' in findings
        assert len(findings['phone_indian']) >= 1
    
    def test_detect_aadhaar(self):
        """Test Aadhaar number detection"""
        detector = PIIDetector()
        text = "My Aadhaar is 1234 5678 9012"
        
        findings = detector.detect_pii(text)
        
        assert 'aadhaar' in findings
        assert len(findings['aadhaar']) == 1
    
    def test_detect_pan(self):
        """Test PAN card detection"""
        detector = PIIDetector()
        text = "PAN number: ABCDE1234F"
        
        findings = detector.detect_pii(text)
        
        assert 'pan' in findings
        assert 'ABCDE1234F' in findings['pan']
    
    def test_detect_ip_address(self):
        """Test IP address detection"""
        detector = PIIDetector()
        text = "Server IP is 192.168.1.1 and backup is 10.0.0.1"
        
        findings = detector.detect_pii(text)
        
        assert 'ip_address' in findings
        assert len(findings['ip_address']) == 2
    
    def test_detect_url(self):
        """Test URL detection"""
        detector = PIIDetector()
        text = "Visit https://example.com or http://test.org"
        
        findings = detector.detect_pii(text)
        
        assert 'url' in findings
        assert len(findings['url']) == 2
    
    def test_detect_potential_names(self):
        """Test name detection"""
        detector = PIIDetector()
        text = "Mr. Ramesh Kumar and Dr. Priya Sharma attended"
        
        findings = detector.detect_pii(text)
        
        assert 'potential_names' in findings
        assert len(findings['potential_names']) >= 1
    
    def test_detect_address_keywords(self):
        """Test address keyword detection"""
        detector = PIIDetector()
        text = "My address is 123 Main Street, Pune"
        
        findings = detector.detect_pii(text)
        
        assert 'potential_address' in findings
    
    def test_no_pii_in_clean_text(self):
        """Test that clean text returns no PII"""
        detector = PIIDetector()
        text = "What is the best fertilizer for wheat crops?"
        
        findings = detector.detect_pii(text)
        
        assert len(findings) == 0
    
    def test_scan_dict_with_pii(self):
        """Test scanning dictionary for PII"""
        detector = PIIDetector()
        data = {
            'query': 'Contact me at test@example.com',
            'response': 'Call 9876543210',
            'metadata': {
                'location': 'Pune'
            }
        }
        
        findings = detector.scan_dict(data)
        
        assert len(findings) >= 2
        assert any('email' in f['pii_types'] for f in findings)
        assert any('phone_indian' in f['pii_types'] for f in findings)
    
    def test_scan_nested_dict(self):
        """Test scanning nested dictionary"""
        detector = PIIDetector()
        data = {
            'conversations': [
                {'query': 'Email: test@example.com'},
                {'query': 'Phone: 9876543210'}
            ]
        }
        
        findings = detector.scan_dict(data)
        
        assert len(findings) == 2


class TestPrivacyAuditor:
    """Test privacy auditor functionality"""
    
    def test_audit_conversation_with_pii(self):
        """Test auditing conversation with PII"""
        auditor = PrivacyAuditor()
        conversation = {
            'timestamp': '2026-03-04T10:00:00',
            'query': 'My email is farmer@example.com',
            'response': 'Thank you',
            'metadata': {}
        }
        
        result = auditor.audit_conversation(conversation)
        
        assert result['has_pii'] is True
        assert result['pii_count'] > 0
        assert len(result['findings']) > 0
    
    def test_audit_conversation_without_pii(self):
        """Test auditing clean conversation"""
        auditor = PrivacyAuditor()
        conversation = {
            'timestamp': '2026-03-04T10:00:00',
            'query': 'What is the best fertilizer for wheat?',
            'response': 'Use NPK fertilizer',
            'metadata': {}
        }
        
        result = auditor.audit_conversation(conversation)
        
        assert result['has_pii'] is False
        assert result['pii_count'] == 0
    
    def test_audit_user_data_with_pii(self):
        """Test auditing user data with PII"""
        auditor = PrivacyAuditor()
        user_data = {
            'user_id': 'test_user',
            'conversations': [
                {
                    'timestamp': '2026-03-04T10:00:00',
                    'query': 'Call me at 9876543210',
                    'response': 'Sure',
                    'metadata': {}
                },
                {
                    'timestamp': '2026-03-04T11:00:00',
                    'query': 'Email: test@example.com',
                    'response': 'Got it',
                    'metadata': {}
                }
            ]
        }
        
        report = auditor.audit_user_data(user_data)
        
        assert report['total_pii_findings'] > 0
        assert report['conversations_with_pii'] == 2
        assert len(report['pii_types_found']) > 0
        assert len(report['recommendations']) > 0
    
    def test_audit_user_data_without_pii(self):
        """Test auditing clean user data"""
        auditor = PrivacyAuditor()
        user_data = {
            'user_id': 'test_user',
            'conversations': [
                {
                    'timestamp': '2026-03-04T10:00:00',
                    'query': 'What crops grow well in monsoon?',
                    'response': 'Rice and sugarcane',
                    'metadata': {}
                }
            ]
        }
        
        report = auditor.audit_user_data(user_data)
        
        assert report['total_pii_findings'] == 0
        assert report['conversations_with_pii'] == 0
        assert 'No PII detected' in ' '.join(report['recommendations'])
    
    def test_audit_detects_sensitive_pii(self):
        """Test detection of sensitive PII (Aadhaar, PAN)"""
        auditor = PrivacyAuditor()
        user_data = {
            'user_id': 'test_user',
            'conversations': [
                {
                    'timestamp': '2026-03-04T10:00:00',
                    'query': 'My Aadhaar is 1234 5678 9012',
                    'response': 'Received',
                    'metadata': {}
                }
            ]
        }
        
        report = auditor.audit_user_data(user_data)
        
        assert 'aadhaar' in report['pii_types_found']
        assert any('CRITICAL' in rec for rec in report['recommendations'])
    
    def test_audit_profile_data(self):
        """Test auditing user profile data"""
        auditor = PrivacyAuditor()
        user_data = {
            'user_id': 'test_user',
            'location': 'Pune',
            'email': 'farmer@example.com',
            'conversations': []
        }
        
        report = auditor.audit_user_data(user_data)
        
        assert report['profile_has_pii'] is True
        assert 'email' in report['pii_types_found']
    
    def test_generate_summary_report(self):
        """Test generating summary report from multiple audits"""
        auditor = PrivacyAuditor()
        
        audit_results = [
            {
                'user_id': 'user1',
                'total_pii_findings': 2,
                'pii_types_found': ['email', 'phone_indian']
            },
            {
                'user_id': 'user2',
                'total_pii_findings': 0,
                'pii_types_found': []
            },
            {
                'user_id': 'user3',
                'total_pii_findings': 1,
                'pii_types_found': ['aadhaar']
            }
        ]
        
        summary = auditor.generate_summary_report(audit_results)
        
        assert summary['total_users_audited'] == 3
        assert summary['users_with_pii'] == 2
        assert summary['total_pii_findings'] == 3
        assert len(summary['high_risk_users']) == 1
        assert summary['high_risk_users'][0]['user_id'] == 'user3'
    
    def test_audit_sample_data_convenience_function(self):
        """Test convenience function for auditing sample data"""
        sample_data = {
            'user_id': 'test_user',
            'conversations': [
                {
                    'timestamp': '2026-03-04T10:00:00',
                    'query': 'Test query',
                    'response': 'Test response',
                    'metadata': {}
                }
            ]
        }
        
        report = audit_sample_data(sample_data)
        
        assert 'audit_timestamp' in report
        assert 'user_id' in report
        assert 'total_pii_findings' in report


class TestPIIPatterns:
    """Test specific PII pattern matching"""
    
    def test_credit_card_detection(self):
        """Test credit card number detection"""
        detector = PIIDetector()
        text = "Card: 1234 5678 9012 3456"
        
        findings = detector.detect_pii(text)
        
        assert 'credit_card' in findings
    
    def test_coordinates_detection(self):
        """Test GPS coordinates detection"""
        detector = PIIDetector()
        text = "Location: 18.5204,73.8567"
        
        findings = detector.detect_pii(text)
        
        assert 'coordinates' in findings
    
    def test_postal_code_detection(self):
        """Test Indian postal code detection"""
        detector = PIIDetector()
        text = "PIN code is 411001"
        
        findings = detector.detect_pii(text)
        
        assert 'postal_code_indian' in findings
    
    def test_multiple_pii_types_in_single_text(self):
        """Test detecting multiple PII types in one text"""
        detector = PIIDetector()
        text = "Contact Mr. Ramesh at 9876543210 or ramesh@example.com, address: 411001"
        
        findings = detector.detect_pii(text)
        
        assert len(findings) >= 3
        assert 'phone_indian' in findings
        assert 'email' in findings
        assert 'potential_names' in findings or 'postal_code_indian' in findings
