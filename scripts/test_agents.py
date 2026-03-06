#!/usr/bin/env python3
"""
GramSetu Agent Testing Script
Tests all 6 agents with various queries to validate functionality
"""

import json
import requests
import time
import base64
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Configuration
API_ENDPOINT = 'https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query'
TEST_USER_ID = 'test_farmer_gramsetu'
TEST_LOCATION = 'Nashik, Maharashtra'

# Test queries for each agent
TEST_QUERIES = {
    'krishak-mitra': [
        {
            'query': 'What is the best time to plant wheat in Maharashtra?',
            'description': 'Crop timing advice',
            'expected_keywords': ['wheat', 'plant', 'season', 'Maharashtra']
        },
        {
            'query': 'How much water does rice crop need per day?',
            'description': 'Irrigation requirements',
            'expected_keywords': ['rice', 'water', 'irrigation']
        },
        {
            'query': 'What are the best organic fertilizers for tomato plants?',
            'description': 'Fertilizer recommendations',
            'expected_keywords': ['organic', 'fertilizer', 'tomato']
        }
    ],
    'rog-nivaarak': [
        {
            'query': 'My tomato leaves have brown spots. What disease is this?',
            'description': 'Disease identification',
            'expected_keywords': ['disease', 'tomato', 'leaf', 'spot']
        },
        {
            'query': 'How to treat powdery mildew on grapes organically?',
            'description': 'Organic treatment',
            'expected_keywords': ['powdery mildew', 'grape', 'organic', 'treatment']
        },
        {
            'query': 'What are common pests affecting cotton crops?',
            'description': 'Pest identification',
            'expected_keywords': ['pest', 'cotton', 'insect']
        }
    ],
    'bazaar-darshi': [
        {
            'query': 'What is the current market price of onions in Nashik?',
            'description': 'Market price query',
            'expected_keywords': ['price', 'onion', 'market', 'Nashik']
        },
        {
            'query': 'Which crops have the best profit margins this season?',
            'description': 'Profit analysis',
            'expected_keywords': ['profit', 'crop', 'margin', 'season']
        },
        {
            'query': 'Where can I sell my wheat harvest for the best price?',
            'description': 'Market connection',
            'expected_keywords': ['sell', 'wheat', 'price', 'market']
        }
    ],
    'sarkar-sahayak': [
        {
            'query': 'What is PM-KISAN scheme and am I eligible?',
            'description': 'Scheme information',
            'expected_keywords': ['PM-KISAN', 'scheme', 'eligible', 'benefit']
        },
        {
            'query': 'How to apply for crop insurance under PMFBY?',
            'description': 'Application process',
            'expected_keywords': ['PMFBY', 'insurance', 'apply', 'crop']
        },
        {
            'query': 'What subsidies are available for drip irrigation?',
            'description': 'Subsidy information',
            'expected_keywords': ['subsidy', 'drip', 'irrigation', 'scheme']
        }
    ],
    'mausam-gyaata': [
        {
            'query': 'What is the weather forecast for Nashik this week?',
            'description': 'Weather forecast',
            'expected_keywords': ['weather', 'forecast', 'Nashik', 'week']
        },
        {
            'query': 'When should I irrigate my crops based on upcoming weather?',
            'description': 'Irrigation timing',
            'expected_keywords': ['irrigate', 'weather', 'crop', 'water']
        },
        {
            'query': 'Is there a risk of frost in the next few days?',
            'description': 'Weather alert',
            'expected_keywords': ['frost', 'temperature', 'risk', 'cold']
        }
    ],
    'krishi-bodh': [
        {
            'query': 'What are the latest farming techniques for water conservation?',
            'description': 'Modern techniques',
            'expected_keywords': ['technique', 'water', 'conservation', 'farming']
        },
        {
            'query': 'How can I improve soil health organically?',
            'description': 'Soil management',
            'expected_keywords': ['soil', 'health', 'organic', 'improve']
        },
        {
            'query': 'What training programs are available for farmers?',
            'description': 'Educational resources',
            'expected_keywords': ['training', 'program', 'farmer', 'education']
        }
    ]
}

# Test image path (optional)
TEST_IMAGE_PATH = 'data/plantvillage/test/test/TomatoEarlyBlight1.JPG'


class AgentTester:
    """Test harness for GramSetu agents"""
    
    def __init__(self, api_endpoint: str, user_id: str, location: str):
        self.api_endpoint = api_endpoint
        self.user_id = user_id
        self.location = location
        self.results = []
        
    def send_query(
        self, 
        query: str, 
        language: str = 'en',
        image_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send a query to the API"""
        payload = {
            'user_id': self.user_id,
            'query': query,
            'language': language,
            'location': self.location
        }
        
        # Add image if provided
        if image_path and Path(image_path).exists():
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                payload['image'] = image_base64
        
        try:
            response = requests.post(
                self.api_endpoint,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'error': str(e),
                'success': False
            }
    
    def validate_response(
        self, 
        response: Dict[str, Any], 
        expected_keywords: List[str]
    ) -> Dict[str, Any]:
        """Validate response contains expected keywords"""
        if 'error' in response:
            return {
                'valid': False,
                'reason': f"API Error: {response['error']}",
                'keywords_found': []
            }
        
        response_text = response.get('response', '').lower()
        keywords_found = [kw for kw in expected_keywords if kw.lower() in response_text]
        
        return {
            'valid': len(keywords_found) > 0,
            'keywords_found': keywords_found,
            'keywords_missing': [kw for kw in expected_keywords if kw.lower() not in response_text],
            'response_length': len(response_text)
        }
    
    def test_agent(self, agent_name: str, test_cases: List[Dict]) -> Dict[str, Any]:
        """Test a specific agent with multiple queries"""
        print(f"\n{'='*80}")
        print(f"Testing Agent: {agent_name.upper()}")
        print(f"{'='*80}")
        
        agent_results = {
            'agent_name': agent_name,
            'total_tests': len(test_cases),
            'passed': 0,
            'failed': 0,
            'test_cases': []
        }
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}/{len(test_cases)}: {test_case['description']}")
            print(f"Query: {test_case['query']}")
            
            start_time = time.time()
            response = self.send_query(test_case['query'])
            response_time = time.time() - start_time
            
            validation = self.validate_response(response, test_case['expected_keywords'])
            
            test_result = {
                'test_number': i,
                'description': test_case['description'],
                'query': test_case['query'],
                'response_time': round(response_time, 2),
                'success': 'error' not in response,
                'validation': validation,
                'agent_used': response.get('agent_used', 'unknown'),
                'response_preview': response.get('response', '')[:200] + '...' if response.get('response') else None
            }
            
            if test_result['success'] and validation['valid']:
                agent_results['passed'] += 1
                print(f"✅ PASSED (Response time: {response_time:.2f}s)")
                print(f"   Agent used: {test_result['agent_used']}")
                print(f"   Keywords found: {', '.join(validation['keywords_found'])}")
            else:
                agent_results['failed'] += 1
                print(f"❌ FAILED")
                if not test_result['success']:
                    print(f"   Error: {response.get('error', 'Unknown error')}")
                else:
                    print(f"   Validation failed: {validation['reason'] if 'reason' in validation else 'No expected keywords found'}")
                    print(f"   Keywords missing: {', '.join(validation['keywords_missing'])}")
            
            if test_result['response_preview']:
                print(f"   Response preview: {test_result['response_preview']}")
            
            agent_results['test_cases'].append(test_result)
            
            # Rate limiting - wait 1 second between requests
            time.sleep(1)
        
        return agent_results
    
    def test_image_upload(self) -> Dict[str, Any]:
        """Test image upload functionality"""
        print(f"\n{'='*80}")
        print("Testing Image Upload Functionality")
        print(f"{'='*80}")
        
        if not Path(TEST_IMAGE_PATH).exists():
            print(f"⚠️  Test image not found: {TEST_IMAGE_PATH}")
            return {
                'success': False,
                'error': 'Test image not found'
            }
        
        print(f"\nUploading image: {TEST_IMAGE_PATH}")
        print("Query: What disease is affecting this plant?")
        
        start_time = time.time()
        response = self.send_query(
            "What disease is affecting this plant?",
            image_path=TEST_IMAGE_PATH
        )
        response_time = time.time() - start_time
        
        result = {
            'success': 'error' not in response,
            'response_time': round(response_time, 2),
            'agent_used': response.get('agent_used', 'unknown'),
            'has_image_analysis': 'image_analysis' in response.get('metadata', {}),
            'response_preview': response.get('response', '')[:300] + '...' if response.get('response') else None
        }
        
        if result['success']:
            print(f"✅ Image upload successful (Response time: {response_time:.2f}s)")
            print(f"   Agent used: {result['agent_used']}")
            print(f"   Has image analysis: {result['has_image_analysis']}")
            if result['response_preview']:
                print(f"   Response preview: {result['response_preview']}")
        else:
            print(f"❌ Image upload failed")
            print(f"   Error: {response.get('error', 'Unknown error')}")
        
        return result
    
    def test_multilingual(self) -> Dict[str, Any]:
        """Test multilingual support"""
        print(f"\n{'='*80}")
        print("Testing Multilingual Support")
        print(f"{'='*80}")
        
        test_languages = [
            ('hi', 'हिंदी', 'What is the best fertilizer for wheat?'),
            ('mr', 'मराठी', 'What is the weather forecast for today?'),
            ('en', 'English', 'How to control pests in cotton?')
        ]
        
        results = []
        
        for lang_code, lang_name, query in test_languages:
            print(f"\nTesting {lang_name} ({lang_code})")
            print(f"Query: {query}")
            
            start_time = time.time()
            response = self.send_query(query, language=lang_code)
            response_time = time.time() - start_time
            
            result = {
                'language': lang_name,
                'language_code': lang_code,
                'success': 'error' not in response,
                'response_time': round(response_time, 2),
                'translated': response.get('metadata', {}).get('translated', False),
                'response_preview': response.get('response', '')[:200] + '...' if response.get('response') else None
            }
            
            if result['success']:
                print(f"✅ {lang_name} test passed (Response time: {response_time:.2f}s)")
                print(f"   Translated: {result['translated']}")
                if result['response_preview']:
                    print(f"   Response preview: {result['response_preview']}")
            else:
                print(f"❌ {lang_name} test failed")
                print(f"   Error: {response.get('error', 'Unknown error')}")
            
            results.append(result)
            time.sleep(1)
        
        return {
            'total_languages': len(test_languages),
            'passed': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success']),
            'results': results
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests"""
        print(f"\n{'#'*80}")
        print(f"# GramSetu Agent Testing Suite")
        print(f"# Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"# API Endpoint: {self.api_endpoint}")
        print(f"# Test User: {self.user_id}")
        print(f"# Location: {self.location}")
        print(f"{'#'*80}")
        
        all_results = {
            'test_suite': 'GramSetu Agents',
            'timestamp': datetime.now().isoformat(),
            'api_endpoint': self.api_endpoint,
            'agents': {},
            'image_upload': None,
            'multilingual': None,
            'summary': {}
        }
        
        # Test each agent
        for agent_name, test_cases in TEST_QUERIES.items():
            agent_results = self.test_agent(agent_name, test_cases)
            all_results['agents'][agent_name] = agent_results
        
        # Test image upload
        all_results['image_upload'] = self.test_image_upload()
        
        # Test multilingual
        all_results['multilingual'] = self.test_multilingual()
        
        # Calculate summary
        total_tests = sum(r['total_tests'] for r in all_results['agents'].values())
        total_passed = sum(r['passed'] for r in all_results['agents'].values())
        total_failed = sum(r['failed'] for r in all_results['agents'].values())
        
        all_results['summary'] = {
            'total_agents': len(TEST_QUERIES),
            'total_tests': total_tests,
            'total_passed': total_passed,
            'total_failed': total_failed,
            'success_rate': round((total_passed / total_tests * 100), 2) if total_tests > 0 else 0,
            'image_upload_success': all_results['image_upload']['success'],
            'multilingual_success_rate': round(
                (all_results['multilingual']['passed'] / all_results['multilingual']['total_languages'] * 100), 2
            )
        }
        
        # Print summary
        self.print_summary(all_results)
        
        # Save results to file
        output_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\n📄 Full results saved to: {output_file}")
        
        return all_results
    
    def print_summary(self, results: Dict[str, Any]):
        """Print test summary"""
        print(f"\n{'='*80}")
        print("TEST SUMMARY")
        print(f"{'='*80}")
        
        summary = results['summary']
        
        print(f"\nAgent Tests:")
        print(f"  Total Agents Tested: {summary['total_agents']}")
        print(f"  Total Test Cases: {summary['total_tests']}")
        print(f"  Passed: {summary['total_passed']} ✅")
        print(f"  Failed: {summary['total_failed']} ❌")
        print(f"  Success Rate: {summary['success_rate']}%")
        
        print(f"\nAgent Breakdown:")
        for agent_name, agent_results in results['agents'].items():
            status = "✅" if agent_results['failed'] == 0 else "⚠️"
            print(f"  {status} {agent_name}: {agent_results['passed']}/{agent_results['total_tests']} passed")
        
        print(f"\nImage Upload:")
        img_status = "✅" if summary['image_upload_success'] else "❌"
        print(f"  {img_status} Image upload test: {'PASSED' if summary['image_upload_success'] else 'FAILED'}")
        
        print(f"\nMultilingual Support:")
        print(f"  Success Rate: {summary['multilingual_success_rate']}%")
        
        print(f"\n{'='*80}")


def main():
    """Main test execution"""
    tester = AgentTester(API_ENDPOINT, TEST_USER_ID, TEST_LOCATION)
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results['summary']['total_failed'] == 0 and results['summary']['image_upload_success']:
        print("\n🎉 All tests passed!")
        exit(0)
    else:
        print(f"\n⚠️  Some tests failed. Check the results above.")
        exit(1)


if __name__ == "__main__":
    main()
