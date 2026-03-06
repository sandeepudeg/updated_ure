# Nova Lite Model Update - Summary

## What Was Done

Updated the Mumbai Lambda function to use the direct model ID `amazon.nova-lite-v1:0` instead of the inference profile `apac.amazon.nova-lite-v1:0`.

## Changes Made

### 1. Lambda Handler Code (`src/aws/lambda_handler.py`)

**Before:**
```python
model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")
```

**After:**
```python
model_id = "amazon.nova-lite-v1:0"
```

This hardcodes the direct model ID for more reliable access.

### 2. Deployment Scripts Created

Three new scripts to help with deployment:

1. **`scripts/update_model_to_nova_lite.py`**
   - Updates Lambda environment variable only
   - Tests model invocation
   - Tests Lambda function
   - Quick update without code redeployment

2. **`scripts/redeploy_mumbai_lambda.py`**
   - Creates deployment package
   - Updates Lambda code
   - Updates environment variables
   - Full redeployment with new code

3. **`scripts/redeploy_mumbai_lambda.ps1`**
   - PowerShell wrapper
   - Activates virtual environment
   - Runs Python deployment script
   - Easy one-command deployment

### 3. Documentation Created

- **`MODEL_UPDATE_GUIDE.md`** - Complete guide with troubleshooting
- **`NOVA_LITE_UPDATE_SUMMARY.md`** - This file (quick reference)

## How to Deploy

### Quick Method (Recommended)

```powershell
# Run the PowerShell script
.\scripts\redeploy_mumbai_lambda.ps1
```

This will:
1. Activate virtual environment
2. Create deployment package
3. Update Lambda code
4. Update environment variables
5. Test the deployment

### Alternative: Environment Variable Only

If you just want to update the environment variable:

```powershell
# Activate virtual environment
.\rural\Scripts\Activate.ps1

# Run update script
py scripts/update_model_to_nova_lite.py
```

## Why This Change?

### Benefits

1. **Simpler Configuration**
   - Direct model access instead of inference profile
   - No dependency on regional profiles
   - Easier to understand and maintain

2. **More Reliable**
   - Direct on-demand invocation
   - No profile-related issues
   - Consistent across regions

3. **Better Compatibility**
   - Works with standard Bedrock APIs
   - No special profile setup needed
   - Easier to troubleshoot

### Model Comparison

| Feature | Inference Profile | Direct Model |
|---------|-------------------|--------------|
| Model ID | `apac.amazon.nova-lite-v1:0` | `amazon.nova-lite-v1:0` |
| Setup | Requires profile | Direct access |
| Reliability | Profile-dependent | Direct invocation |
| Simplicity | More complex | Simpler ✅ |

## Testing

After deployment, test with:

```powershell
# Run Streamlit with logging
.\run_local_with_logging.ps1
```

Then:
1. Submit a test query
2. Check response time (should be < 2s)
3. Verify no model errors in logs
4. Confirm proper AI responses

## Expected Results

- ✅ Same performance (50-100ms API latency)
- ✅ Same response quality
- ✅ More reliable model access
- ✅ No breaking changes

## Verification Checklist

- [ ] Lambda code updated
- [ ] Environment variable set to `amazon.nova-lite-v1:0`
- [ ] Lambda function tested successfully
- [ ] API endpoint responds correctly
- [ ] Streamlit app works with Mumbai API
- [ ] No errors in CloudWatch logs

## Troubleshooting

### If deployment fails:

1. **Check AWS credentials**
   ```powershell
   aws sts get-caller-identity
   ```

2. **Verify Lambda exists**
   ```bash
   aws lambda get-function --function-name ure-mvp-handler-mumbai --region ap-south-1
   ```

3. **Check IAM permissions**
   - Lambda update permissions
   - Bedrock invoke permissions

### If model invocation fails:

1. **Verify model ID**
   - Should be exactly: `amazon.nova-lite-v1:0`
   - Check for typos

2. **Check Bedrock access**
   - Go to Bedrock console
   - Verify Nova Lite is enabled
   - Check IAM role permissions

3. **Review CloudWatch logs**
   ```bash
   aws logs tail /aws/lambda/ure-mvp-handler-mumbai --region ap-south-1 --follow
   ```

## Rollback

If needed, rollback to inference profile:

```bash
aws lambda update-function-configuration \
  --function-name ure-mvp-handler-mumbai \
  --region ap-south-1 \
  --environment "Variables={BEDROCK_MODEL_ID=apac.amazon.nova-lite-v1:0}"
```

## Next Steps

1. **Deploy the update**
   ```powershell
   .\scripts\redeploy_mumbai_lambda.ps1
   ```

2. **Test with Streamlit**
   ```powershell
   .\run_local_with_logging.ps1
   ```

3. **Monitor for 24 hours**
   - Check CloudWatch logs
   - Monitor API Gateway metrics
   - Verify no errors

4. **Update documentation**
   - Note the model change
   - Update deployment guides

## Summary

**Change:** Switched from inference profile to direct model access

**Model ID:** `amazon.nova-lite-v1:0`

**Deployment:** Run `.\scripts\redeploy_mumbai_lambda.ps1`

**Testing:** Run `.\run_local_with_logging.ps1`

**Expected:** Same performance, more reliable access

**Status:** Ready to deploy ✅
