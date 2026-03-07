#!/usr/bin/env python3
"""
Load Testing Script for GramSetu
Tests concurrent users and measures performance under load
"""

import requests
import time
import json
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Configuration
API_ENDPOINT = "https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query"
WEB_URL = "https://d3v7khazsfb4vd.cloudfront.net"

# Test queries
TEST_QUERIES = [
    "What are the current mandi prices for wheat?",
    "Tell me about PM-KISAN scheme",
    "How can I identify tomato leaf disease?",
    "What is the weather forecast for Maharashtra?",
    "Which crops are best for monsoon season?",
]

def test_api_request(query_text, test_id):
    """Test a single API request"""
    start_time = time.time()
    
    try:
        response = requests.post(
            API_ENDPOINT,
            json={
                "user_id": f"load_test_user_{test_id % 10}",
                "query": query_text
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to ms
        
        return {
            "test_id": test_id,
            "query": query_text,
            "status_code": response.status_code,
            "response_time": response_time,
            "success": response.status_code == 200,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        return {
            "test_id": test_id,
            "query": query_text,
            "status_code": 0,
            "response_time": response_time,
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def run_load_test(num_users=200, requests_per_user=40):
    """Run load test with concurrent users"""
    print(f"\n{'='*50}")
    print(f"  GramSetu Load Test")
    print(f"{'='*50}\n")
    print(f"Concurrent Users: {num_users}")
    print(f"Requests per User: {requests_per_user}")
    print(f"Total Requests: {num_users * requests_per_user}\n")
    
    results = []
    test_id = 0
    
    # Create test tasks
    tasks = []
    for user in range(num_users):
        for req in range(requests_per_user):
            query = TEST_QUERIES[test_id % len(TEST_QUERIES)]
            tasks.append((query, test_id))
            test_id += 1
    
    # Execute tests concurrently
    print("Running tests...")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=num_users) as executor:
        futures = [executor.submit(test_api_request, query, tid) for query, tid in tasks]
        
        completed = 0
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            completed += 1
            
            if completed % 10 == 0:
                print(f"  Completed: {completed}/{len(tasks)}")
    
    end_time = time.time()
    total_duration = end_time - start_time
    
    # Analyze results
    print(f"\n{'='*50}")
    print(f"  Test Results")
    print(f"{'='*50}\n")
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    response_times = [r["response_time"] for r in successful]
    
    metrics = {
        "test_config": {
            "concurrent_users": num_users,
            "requests_per_user": requests_per_user,
            "total_requests": len(results),
            "test_duration": round(total_duration, 2)
        },
        "results": {
            "total_requests": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": round((len(successful) / len(results)) * 100, 2) if results else 0
        },
        "performance": {},
        "throughput": {
            "requests_per_second": round(len(results) / total_duration, 2),
            "avg_concurrent": num_users
        },
        "timestamp": datetime.now().isoformat()
    }
    
    if response_times:
        metrics["performance"] = {
            "avg_response_time": round(statistics.mean(response_times), 2),
            "min_response_time": round(min(response_times), 2),
            "max_response_time": round(max(response_times), 2),
            "median_response_time": round(statistics.median(response_times), 2),
            "p95_response_time": round(statistics.quantiles(response_times, n=20)[18], 2),
            "p99_response_time": round(statistics.quantiles(response_times, n=100)[98], 2),
        }
    
    # Print summary
    print(f"Total Requests: {metrics['results']['total_requests']}")
    print(f"Successful: {metrics['results']['successful']}")
    print(f"Failed: {metrics['results']['failed']}")
    print(f"Success Rate: {metrics['results']['success_rate']}%")
    print(f"\nPerformance:")
    if metrics["performance"]:
        print(f"  Avg Response Time: {metrics['performance']['avg_response_time']}ms")
        print(f"  Min Response Time: {metrics['performance']['min_response_time']}ms")
        print(f"  Max Response Time: {metrics['performance']['max_response_time']}ms")
        print(f"  P95 Response Time: {metrics['performance']['p95_response_time']}ms")
        print(f"  P99 Response Time: {metrics['performance']['p99_response_time']}ms")
    print(f"\nThroughput:")
    print(f"  Requests/Second: {metrics['throughput']['requests_per_second']}")
    print(f"  Test Duration: {metrics['test_config']['test_duration']}s")
    
    # Save results
    output_file = "deployment/load-test-results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "metrics": metrics,
            "detailed_results": results
        }, f, indent=2)
    
    print(f"\n✓ Results saved to: {output_file}")
    print()
    
    return metrics

if __name__ == "__main__":
    import sys
    
    # Parse arguments
    num_users = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    requests_per_user = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    
    # Run test
    run_load_test(num_users, requests_per_user)
