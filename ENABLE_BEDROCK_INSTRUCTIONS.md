# Enable Bedrock Models - Simple Instructions

## The Problem
Your Bedrock models are not enabled in ANY region. This is why you're getting "Operation not allowed" errors.

## The Solution (Takes 2 minutes)

### Step 1: Go to Bedrock Playground
Open this link in your browser:
**https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/chat-playground**

### Step 2: Select a Model
1. Look for the "Select model" dropdown at the top
2. Click it and search for "Amazon Nova Pro"
3. Select "Amazon Nova Pro"

### Step 3: Send a Test Message
1. In the chat box, type: "Hello"
2. Click the "Run" button
3. You should get a response

**This action automatically enables the model for your entire AWS account!**

### Step 4: Restart Streamlit
```powershell
# Kill existing Streamlit
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Start fresh
streamlit run src/ui/app.py
```

### Step 5: Test
Open http://localhost:8501 and try a query.

## Why This Works
AWS changed their policy - models are now "auto-enabled" when you first use them in the playground. This is the easiest way to enable them.

## Current Configuration
- ✅ Streamlit app: Fixed and ready
- ✅ API endpoint: https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query
- ❌ Bedrock models: NOT ENABLED (you need to do Step 1-3 above)

## After Enabling
Once you enable the model in the playground, both your us-east-1 and ap-south-1 deployments should work immediately.
