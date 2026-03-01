# AWS CLI Reconfiguration Guide

## Your Current Credentials Are Invalid

The error "InvalidClientTokenId" means your AWS credentials have expired or are incorrect.

## Reconfigure AWS CLI

Run this command:

```powershell
aws configure
```

When prompted, enter:

1. **AWS Access Key ID**: `[YOUR_ACCESS_KEY_ID]`
2. **AWS Secret Access Key**: `[YOUR_SECRET_ACCESS_KEY]`
3. **Default region name**: `us-east-1`
4. **Default output format**: `json`

## Verify Configuration

After configuring, test it:

```powershell
aws sts get-caller-identity
```

You should see:
```json
{
    "UserId": "188238313375",
    "Account": "188238313375",
    "Arn": "arn:aws:iam::188238313375:root"
}
```

## Alternative: Manual Configuration

If `aws configure` doesn't work, manually edit the files:

### 1. Edit credentials file:
```powershell
notepad C:\Users\sande\.aws\credentials
```

Add:
```
[default]


### 2. Edit config file:
```powershell
notepad C:\Users\sande\.aws\config
```

Add:
```
[default]
region = us-east-1
output = json
```

## After Reconfiguring

1. Test AWS access:
   ```powershell
   aws sts get-caller-identity
   ```

2. Test Bedrock:
   ```powershell
   py scripts/check_us_east_bedrock.py
   ```

3. If Bedrock still shows "Operation not allowed", go to:
   https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/chat-playground
   
   And send a test message with Amazon Nova Pro selected.

## Current Status

- ✅ Streamlit app: Running at http://localhost:8501
- ✅ API endpoint: Configured for us-east-1
- ❌ AWS credentials: Need to be reconfigured
- ❌ Bedrock model: Needs to be enabled in playground
