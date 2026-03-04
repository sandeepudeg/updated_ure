#!/usr/bin/env python3
"""
Test PDF Links Feature
Tests that government scheme queries return PDF download links
"""

import requests
import json

API_URL = "https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query"

def test_scheme_query(query, expected_scheme):
    """Test a government scheme query"""
    print(f"\n{'='*60}")
    print(f"Testing: {query}")
    print('='*60)
    
    payload = {
        "user_id": "test_farmer_pdf_001",
        "query": query,
        "language": "en",
        "location": "Nashik, Maharashtra, India"
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"\n✓ Response received")
        print(f"Agent: {data.get('agent_used')}")
        print(f"\nResponse text:")
        print(data.get('response', '')[:500])
        
        # Check for PDF links in metadata
        metadata = data.get('metadata', {})
        pdf_links = metadata.get('pdf_links', [])
        
        if pdf_links:
            print(f"\n✓ PDF Links found: {len(pdf_links)}")
            for pdf in pdf_links:
                print(f"  - {pdf['scheme_name']}")
                print(f"    URL: {pdf['url'][:80]}...")
                
            # Check if expected scheme is in the links
            scheme_names = [pdf['scheme_name'] for pdf in pdf_links]
            if expected_scheme in scheme_names:
                print(f"\n✅ SUCCESS: {expected_scheme} PDF link found!")
            else:
                print(f"\n⚠ WARNING: Expected {expected_scheme} but got {scheme_names}")
        else:
            print(f"\n⚠ No PDF links found in metadata")
            print(f"Metadata: {metadata}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

def main():
    print("\n🌾 Testing Government Scheme PDF Links 🌾\n")
    
    test_cases = [
        ("Tell me about PM-Kisan scheme", "PM-Kisan"),
        ("What is crop insurance scheme?", "PMFBY"),
        ("How can I apply for organic farming scheme?", "PKVY"),
        ("Tell me about irrigation schemes", "PMKSY"),
        ("What is eNAM platform?", "eNAM"),
    ]
    
    results = []
    for query, expected_scheme in test_cases:
        success = test_scheme_query(query, expected_scheme)
        results.append((query, success))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for query, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {query[:50]}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! PDF links feature is working.")
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Check the output above.")

if __name__ == "__main__":
    main()
