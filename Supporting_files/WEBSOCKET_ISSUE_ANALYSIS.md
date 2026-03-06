# WebSocket 403 Error Analysis - Singapore App Runner

## Issue Summary

The Singapore App Runner deployment (`https://mysghsfntp.ap-southeast-1.awsapprunner.com`) is experiencing WebSocket connection failures that prevent the Streamlit app from loading.

## Error Details

```
WebSocket connection to 'wss://mysghsfntp.ap-southeast-1.awsapprunner.com/_stcore/stream' failed: 
Error during WebSocket handshake: Unexpected response code: 403
```

**Frequency:** Continuous retries (20+ attempts visible in console)
**Impact:** App stuck in loading state, no content displayed
**User Experience:** Page loads indefinitely (10+ minutes with no progress)

## Root Cause Analysis

### Why This Happens

1. **Streamlit Architecture**
   - Streamlit uses WebSocket for real-time communication between frontend and backend
   - The `/_stcore/stream` endpoint is critical for app functionality
   - Without WebSocket, the app cannot render or respond to user interactions

2. **App Runner Limitation**
   - AWS App Runner has default configurations that may not properly support WebSocket
   - The 403 Forbidden error indicates the WebSocket handshake is being rejected
   - This is likely due to missing headers or incorrect routing configuration

3. **Protocol Mismatch**
   - HTTP/HTTPS works fine (static assets load)
   - WebSocket (WSS) connections are being blocked
   - App Runner may need explicit WebSocket support configuration

## Technical Details

### WebSocket Handshake Process

1. Client initiates WebSocket connection to `wss://mysghsfntp.ap-southeast-1.awsapprunner.com/_stcore/stream`
2. Server should respond with HTTP 101 Switching Protocols
3. Instead, server responds with HTTP 403 Forbidden
4. Connection fails, Streamlit cannot establish real-time communication
5. App remains in loading state indefinitely

### Required Headers for WebSocket

```
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: [random key]
Sec-WebSocket-Version: 13
```

### Expected Response

```
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: [computed key]
```

### Actual Response

```
HTTP/1.1 403 Forbidden
```

## Why Local Deployment Works

**Local Streamlit (port 8501):**
- Direct connection to Streamlit server
- No proxy or load balancer in between
- WebSocket works natively
- Full control over server configuration

**Result:** Instant loading (< 1 second), full functionality

## Why Singapore App Runner Fails

**App Runner Deployment:**
- Managed service with abstracted networking
- May have proxy/load balancer that doesn't support WebSocket
- Limited configuration options for WebSocket
- Default settings block WebSocket handshakes

**Result:** WebSocket 403 errors, app never loads

## Comparison: CloudFront vs App Runner

### CloudFront Issue (Previously Encountered)
- **Problem:** Host header mismatch
- **Symptom:** 404 errors on all requests
- **Cause:** CloudFront sends its own domain, App Runner expects original domain
- **Status:** Abandoned due to complexity

### App Runner WebSocket Issue (Current)
- **Problem:** WebSocket handshake rejection
- **Symptom:** 403 errors on WebSocket connections
- **Cause:** App Runner doesn't properly support WebSocket protocol
- **Status:** Investigating solutions

## Potential Solutions

### Solution 1: Local Deployment (Recommended) ✅

**Pros:**
- Works immediately
- Fast loading (< 1 second)
- No WebSocket issues
- Uses Mumbai API backend (fast from India)
- No additional AWS costs

**Cons:**
- Requires local machine to be running
- Not accessible from other devices
- No public URL

**Implementation:**
```powershell
.\run_local_with_logging.ps1
```

### Solution 2: Update Streamlit Configuration

**Approach:** Modify Streamlit config to work with App Runner

**Changes to try:**
```toml
[server]
enableWebsocketCompression = false
enableCORS = true
allowWebsocketOrigin = ["mysghsfntp.ap-southeast-1.awsapprunner.com"]
```

**Status:** Partially implemented, needs testing

**Likelihood of success:** Low (App Runner limitation, not Streamlit config)

### Solution 3: Migrate to ECS with ALB

**Approach:** Deploy Streamlit on ECS with Application Load Balancer

**Why this works:**
- ALB has native WebSocket support
- Proper protocol upgrade handling
- Full control over routing rules
- Proven to work with Streamlit

**Steps:**
1. Create ECS cluster
2. Create task definition with Streamlit container
3. Create ALB with WebSocket support
4. Configure target group with health checks
5. Deploy ECS service

**Pros:**
- Reliable WebSocket support
- Scalable and production-ready
- Full AWS integration
- Can deploy in any region

**Cons:**
- More complex setup
- Higher cost than App Runner
- More infrastructure to manage

### Solution 4: Use EC2 with Nginx

**Approach:** Deploy on EC2 with Nginx reverse proxy

**Configuration:**
```nginx
location /_stcore/stream {
    proxy_pass http://localhost:8501;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
}
```

**Pros:**
- Full control over configuration
- Proven WebSocket support
- Can deploy in Mumbai region

**Cons:**
- Manual server management
- Need to handle scaling
- Security updates required

### Solution 5: Try App Runner with Custom Domain

**Approach:** Use custom domain with App Runner

**Theory:** Custom domain might bypass WebSocket restrictions

**Steps:**
1. Register domain or use existing
2. Configure custom domain in App Runner
3. Update DNS records
4. Test WebSocket connections

**Likelihood of success:** Low (underlying issue remains)

## Recommended Action Plan

### Immediate (Today)

1. **Use local deployment** with Mumbai API backend
   - Run: `.\run_local_with_logging.ps1`
   - Verify fast loading and full functionality
   - Use for testing and development

2. **Monitor logs** to understand performance
   - Check terminal output for timing information
   - Verify API calls to Mumbai are fast (< 2s)
   - Confirm no WebSocket errors locally

### Short-term (This Week)

1. **Test Streamlit config changes**
   - Deploy updated config to Singapore App Runner
   - Check if WebSocket errors persist
   - Document results

2. **Evaluate ECS migration**
   - Estimate cost of ECS + ALB
   - Compare with App Runner cost
   - Decide if migration is worth it

### Long-term (Next Week)

1. **If WebSocket issue persists:**
   - Migrate to ECS with ALB in Singapore
   - Or deploy to EC2 in Mumbai region
   - Implement proper production setup

2. **If local deployment is sufficient:**
   - Keep using local deployment
   - Delete Singapore App Runner to save costs
   - Focus on backend optimization

## Cost Considerations

### Current Costs

**Singapore App Runner:**
- Service: ~$25/month (running but not functional)
- ECR storage: ~$1/month
- **Total:** ~$26/month for non-working deployment

**Mumbai Lambda + API Gateway:**
- Lambda: ~$5/month (based on usage)
- API Gateway: ~$3/month
- DynamoDB: ~$2/month
- **Total:** ~$10/month (working perfectly)

### Proposed Costs

**Option 1: Local Deployment**
- Cost: $0 (uses existing Mumbai backend)
- Savings: $26/month

**Option 2: ECS + ALB (Singapore)**
- ECS: ~$30/month
- ALB: ~$20/month
- ECR: ~$1/month
- **Total:** ~$51/month

**Option 3: EC2 (Mumbai)**
- t3.small: ~$15/month
- Elastic IP: ~$3/month
- **Total:** ~$18/month

## Performance Comparison

| Deployment | Load Time | API Latency | WebSocket | Cost/Month |
|------------|-----------|-------------|-----------|------------|
| Local + Mumbai API | < 1s | 50-100ms | ✅ Works | $0 |
| Singapore App Runner | Never loads | N/A | ❌ 403 Error | $26 |
| US East App Runner | 10+ min | 200-300ms | ⚠️ Slow | $26 |
| ECS + ALB (Singapore) | < 2s | 50-100ms | ✅ Works | $51 |
| EC2 (Mumbai) | < 2s | 50-100ms | ✅ Works | $18 |

## Conclusion

The WebSocket 403 error on Singapore App Runner is a fundamental compatibility issue between Streamlit's WebSocket requirements and App Runner's default configuration. 

**Best solution for now:** Use local deployment with Mumbai API backend for instant loading and full functionality at zero additional cost.

**If public URL is required:** Migrate to ECS with ALB or EC2 with Nginx for reliable WebSocket support.

**Not recommended:** Continuing to troubleshoot App Runner WebSocket issues, as the service may not be designed to support WebSocket properly.

## References

- [Streamlit WebSocket Documentation](https://docs.streamlit.io/)
- [AWS App Runner Networking](https://docs.aws.amazon.com/apprunner/latest/dg/network.html)
- [WebSocket Protocol RFC 6455](https://tools.ietf.org/html/rfc6455)
- [ALB WebSocket Support](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-listeners.html#websocket-support)
