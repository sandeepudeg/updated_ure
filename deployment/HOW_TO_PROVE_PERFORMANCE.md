# How to Prove Performance with Real Data

## Quick Start (3 Steps)

### 1. Collect Real Metrics from AWS
```powershell
.\scripts\collect-performance-metrics.ps1
```
Collects actual data from CloudWatch and tests live system.

### 2. Run Load Test
```powershell
python scripts/load_test.py 50 10
```
Tests with 50 concurrent users, 10 requests each.

### 3. Generate Report
```powershell
.\scripts\generate-performance-report.ps1
```
Creates HTML report with real data and timestamp.

## What Gets Measured

- Lambda response times from CloudWatch
- API endpoint performance (10 test requests)
- Web page load time
- Error rates and success rates
- Concurrent user handling
- Throughput (requests/second)

## Proof Files Generated

1. `performance-metrics.json` - Raw AWS data
2. `load-test-results.json` - Load test results
3. `gramsetu-performance-report-actual.html` - Visual report

## Requirements

- AWS CLI installed and configured
- Python 3.x with requests library
- AWS credentials with CloudWatch access

## Live Demo During Presentation

1. Open: https://d3v7khazsfb4vd.cloudfront.net
2. Show application working
3. Run: `.\scripts\collect-performance-metrics.ps1`
4. Show real metrics collected
5. Display generated report with timestamp

All data is real and verifiable!
