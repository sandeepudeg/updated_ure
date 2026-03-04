#!/usr/bin/env python3
"""
Test Rural Tourism Agent
Tests tourism-related queries
"""

import requests
import json

API_URL = "https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query"

def test_tourism_query(query):
    """Test a tourism query"""
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print('='*60)
    
    payload = {
        "user_id": "test_farmer_tourism_001",
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
        print(f"\nResponse:")
        print(data.get('response', ''))
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

def main():
    print("\n🏞️ Testing Rural Tourism Agent 🏞️\n")
    
    test_queries = [
        "What festivals happen in Nashik in October?",
        "What historical places can I visit near Nashik?",
        "How can I start a homestay on my farm?",
        "What is agri-tourism and how much can I earn?",
        "Tell me about Trimbakeshwar Temple",
        "What handicrafts are famous in Maharashtra?",
        "How much does it cost to start farm tours?",
    ]
    
    results = []
    for query in test_queries:
        success = test_tourism_query(query)
        results.append((query, success))
        print("\n" + "-"*60)
    
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
        print("\n🎉 All tests passed! Rural Tourism Agent is working.")
    else:
        print(f"\n⚠ {total - passed} test(s) failed.")

if __name__ == "__main__":
    main()
