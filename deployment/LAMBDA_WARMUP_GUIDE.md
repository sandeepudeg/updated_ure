# Lambda Warm-Up Guide

## Why Warm Up Lambda?

Lambda functions experience "cold starts" - the first request after being idle takes significantly longer (3-5 seconds for Docker containers) because AWS needs to:
1. Provision compute resources
2. Download and extract the container image
3. Initialize the runtime environment
4. Load dependencies and code

Subsequent requests are much faster (1-2 seconds) because the Lambda instance stays warm.

## Impact on Performance Scores

### Without Warm-Up (Cold Start)
```
Response Time: 5000ms (5 seconds)
Performance Score: 50/100

Breakdown:
- Response Time: 10/40 points (> 3 seconds)
- Success Rate: 30/30 points (100%)
- Error Rate: 0/20 points (no CloudWatch data)
- Web Load: 10/10 points (< 1 second)
```

### With Warm-Up
```
Response Time: 1500ms (1.5 seconds)
Performance Score: 80/100

Breakdown:
- Response Time: 30/40 points (< 2 seconds)
- Success Rate: 30/30 points (100%)
- Error Rate: 10/20 points (< 1% errors)
- Web Load: 10/10 points (< 1 second)
```

**Improvement: 60% faster response time, 30-point score increase!**

## How to Use

### Option 1: Standalone Warm-Up Script

Warm up Lambda before running any tests:

```powershell
.\scripts\warmup-lambda.ps1
```

**Parameters:**
- `-ApiEndpoint`: API endpoint URL (default: your deployed endpoint)
- `-WarmupRequests`: Number of warm-up requests (default: 3)
- `-DelayBetweenRequests`: Seconds between requests (default: 2)

**Example:**
```powershell
# Warm up with 5 requests
.\scripts\warmup-lambda.ps1 -WarmupRequests 5

# Custom endpoint
.\scripts\warmup-lambda.ps1 -ApiEndpoint "https://your-api.com/query"
```

### Option 2: Automated Performance Testing with Warm-Up

Run the complete workflow with automatic warm-up:

```powershell
.\scripts\run-performance-tests-with-warmup.ps1
```

This will:
1. Warm up Lambda (3 requests)
2. Wait for stabilization (5 seconds)
3. Collect performance metrics
4. Optionally run load tests
5. Generate HTML report

### Option 3: Integrated in Main Test Suite

The main test suite now includes warm-up:

```powershell
.\RUN_ALL_PERFORMANCE_TESTS.ps1
```

It will automatically warm up Lambda before collecting metrics.

## Warm-Up Output

```
========================================
  Lambda Warm-Up
========================================

Warming up Lambda function...
  Endpoint: https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query
  Warm-up requests: 3

  Request 1/3... 4523ms ✓
  Request 2/3... 1876ms ✓
  Request 3/3... 1234ms ✓

Warm-Up Results:
  Successful: 3/3
  Avg Time: 2544.33ms
  Min Time: 1234ms
  Max Time: 4523ms

Warm-Up Analysis:
  First Request: 4523ms (cold start)
  Last Request: 1234ms (warm)
  Improvement: 3289ms (72.7% faster) ✓

✓ Lambda is warmed up and ready for testing!

Done!
```

## Understanding the Results

### Cold Start Indicators
- First request > 3 seconds
- Large improvement between first and last request
- "Inactive" Lambda state in diagnostics

### Warm Lambda Indicators
- Consistent response times (1-2 seconds)
- Minimal improvement between requests
- Response times stable across multiple tests

### Warm-Up Effectiveness

**Excellent (> 60% improvement):**
- First request: 4-5 seconds
- Last request: 1-2 seconds
- Lambda is fully warmed up

**Good (30-60% improvement):**
- First request: 3-4 seconds
- Last request: 2-3 seconds
- Lambda is warming up

**Minimal (< 30% improvement):**
- Consistent times across all requests
- Lambda was already warm
- Or Lambda has performance issues

## Best Practices

### 1. Always Warm Up Before Performance Testing
```powershell
# Bad: Cold start affects results
.\scripts\collect-performance-metrics.ps1

# Good: Warm up first
.\scripts\warmup-lambda.ps1
.\scripts\collect-performance-metrics.ps1
```

### 2. Wait Between Warm-Up and Testing
```powershell
.\scripts\warmup-lambda.ps1
Start-Sleep -Seconds 5  # Let Lambda stabilize
.\scripts\collect-performance-metrics.ps1
```

### 3. Warm Up Multiple Instances for Load Testing
```powershell
# Warm up with more requests for concurrent testing
.\scripts\warmup-lambda.ps1 -WarmupRequests 10
python scripts/load_test.py 50 5
```

### 4. Re-Warm If Lambda Goes Idle
Lambda instances stay warm for 5-15 minutes. If you wait too long between tests, warm up again:

```powershell
# Test 1
.\scripts\warmup-lambda.ps1
.\scripts\collect-performance-metrics.ps1

# Wait 20 minutes...

# Test 2 - Warm up again!
.\scripts\warmup-lambda.ps1
.\scripts\collect-performance-metrics.ps1
```

## Troubleshooting

### Warm-Up Fails
```
✗ Warm-up failed! All requests failed.
```

**Solutions:**
1. Check API endpoint is correct
2. Verify Lambda function is deployed
3. Check AWS credentials
4. Run diagnostic: `.\scripts\diagnose-api.ps1`

### No Improvement After Warm-Up
```
Improvement: Minimal
```

**Possible Causes:**
1. Lambda was already warm
2. Lambda has performance issues (check CloudWatch logs)
3. Bedrock API is slow (not Lambda's fault)
4. Network latency

### Warm-Up Times Still Slow (> 3 seconds)
```
Last Request: 3500ms (warm)
```

**Solutions:**
1. Increase Lambda memory (more CPU = faster)
2. Optimize code (reduce dependencies)
3. Enable Provisioned Concurrency (keeps Lambda always warm)
4. Check Bedrock API performance

## Advanced: Provisioned Concurrency

For production systems that need consistently fast response times, enable Provisioned Concurrency:

```bash
# Keep 2 Lambda instances always warm
aws lambda put-provisioned-concurrency-config \
  --function-name ure-mvp-handler-docker \
  --provisioned-concurrent-executions 2
```

**Benefits:**
- Zero cold starts
- Consistent response times (1-2 seconds)
- Better user experience

**Costs:**
- ~$0.015/hour per instance
- ~$22/month for 2 instances
- Worth it for production!

## Performance Testing Workflow

### Recommended Workflow
```powershell
# 1. Diagnose (optional, if having issues)
.\scripts\diagnose-api.ps1

# 2. Warm up Lambda
.\scripts\warmup-lambda.ps1

# 3. Collect metrics
.\scripts\collect-performance-metrics.ps1

# 4. Load test
python scripts/load_test.py 10 5

# 5. Generate report
.\scripts\generate-performance-report.ps1
```

### Quick Workflow (Automated)
```powershell
# All-in-one with warm-up
.\scripts\run-performance-tests-with-warmup.ps1
```

### Full Workflow (Interactive)
```powershell
# Interactive with all options
.\RUN_ALL_PERFORMANCE_TESTS.ps1
```

## Expected Results

### Before Warm-Up
- Response Time: 4-5 seconds
- Performance Score: 40-50/100
- Inconsistent times

### After Warm-Up
- Response Time: 1-2 seconds
- Performance Score: 70-85/100
- Consistent times

### With Provisioned Concurrency
- Response Time: 1-1.5 seconds
- Performance Score: 85-95/100
- Always consistent

## Summary

Warming up Lambda before performance testing is essential for accurate results. It eliminates cold start delays and provides realistic performance metrics that reflect actual user experience after the first request.

Use the warm-up scripts to ensure your performance tests show the true capabilities of your system!
