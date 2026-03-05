# Configure New AWS Credentials
# This script helps you set up new AWS access keys after rotation

Write-Host "=== AWS Credentials Configuration ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check current AWS configuration
Write-Host "Step 1: Checking current AWS configuration..." -ForegroundColor Yellow
Write-Host ""

$awsConfigured = $false
try {
    $currentIdentity = aws sts get-caller-identity 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Current AWS Identity:" -ForegroundColor Green
        $currentIdentity | ConvertFrom-Json | Format-List
        $awsConfigured = $true
    }
} catch {
    Write-Host "No valid AWS credentials found" -ForegroundColor Yellow
}

Write-Host ""

# Step 2: Guide user to create new keys
Write-Host "Step 2: Create New Access Keys in AWS Console" -ForegroundColor Yellow
Write-Host ""
Write-Host "Please follow these steps:" -ForegroundColor Cyan
Write-Host "  1. Open AWS Console: https://console.aws.amazon.com/" -ForegroundColor Gray
Write-Host "  2. Go to: IAM → Users → [Your Username] → Security Credentials" -ForegroundColor Gray
Write-Host "  3. Under 'Access keys', click 'Create access key'" -ForegroundColor Gray
Write-Host "  4. Select use case: 'Command Line Interface (CLI)'" -ForegroundColor Gray
Write-Host "  5. Add description tag: 'Rotated after credential exposure - $(Get-Date -Format 'yyyy-MM-dd')'" -ForegroundColor Gray
Write-Host "  6. Click 'Create access key'" -ForegroundColor Gray
Write-Host "  7. IMPORTANT: Download the .csv file or copy the keys (you won't see them again!)" -ForegroundColor Red
Write-Host ""

$continue = Read-Host "Have you created new access keys? (yes/no)"
if ($continue -ne "yes") {
    Write-Host "Please create new access keys first, then run this script again." -ForegroundColor Yellow
    exit 0
}

Write-Host ""

# Step 3: Configure AWS CLI
Write-Host "Step 3: Configure AWS CLI with new credentials" -ForegroundColor Yellow
Write-Host ""
Write-Host "You can configure AWS credentials in two ways:" -ForegroundColor Cyan
Write-Host ""
Write-Host "OPTION 1: Use AWS CLI configure command (Recommended)" -ForegroundColor Green
Write-Host "  Run: aws configure" -ForegroundColor Gray
Write-Host ""
Write-Host "OPTION 2: Manually edit credentials file" -ForegroundColor Green
Write-Host "  File location: $env:USERPROFILE\.aws\credentials" -ForegroundColor Gray
Write-Host ""

$method = Read-Host "Choose method (1 or 2)"

if ($method -eq "1") {
    Write-Host ""
    Write-Host "Running 'aws configure'..." -ForegroundColor Yellow
    Write-Host "Please enter your new credentials when prompted:" -ForegroundColor Cyan
    Write-Host ""
    
    aws configure
    
} elseif ($method -eq "2") {
    Write-Host ""
    Write-Host "Opening credentials file for manual editing..." -ForegroundColor Yellow
    
    $credentialsPath = "$env:USERPROFILE\.aws\credentials"
    
    # Create .aws directory if it doesn't exist
    $awsDir = "$env:USERPROFILE\.aws"
    if (-not (Test-Path $awsDir)) {
        New-Item -ItemType Directory -Path $awsDir -Force | Out-Null
        Write-Host "Created .aws directory" -ForegroundColor Green
    }
    
    # Create credentials file if it doesn't exist
    if (-not (Test-Path $credentialsPath)) {
        $template = @"
[default]
aws_access_key_id = YOUR_ACCESS_KEY_ID
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY
region = us-east-1
"@
        Set-Content -Path $credentialsPath -Value $template
        Write-Host "Created credentials file with template" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "Credentials file location: $credentialsPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Edit the file with this format:" -ForegroundColor Yellow
    Write-Host @"
[default]
aws_access_key_id = YOUR_NEW_ACCESS_KEY_ID
aws_secret_access_key = YOUR_NEW_SECRET_ACCESS_KEY
region = us-east-1
"@ -ForegroundColor Gray
    
    Write-Host ""
    $openFile = Read-Host "Open file in notepad? (yes/no)"
    if ($openFile -eq "yes") {
        notepad $credentialsPath
    }
    
    Write-Host ""
    Write-Host "Press Enter after you've saved your changes..." -ForegroundColor Yellow
    Read-Host
}

Write-Host ""

# Step 4: Verify new credentials
Write-Host "Step 4: Verifying new credentials..." -ForegroundColor Yellow
Write-Host ""

try {
    $newIdentity = aws sts get-caller-identity 2>&1 | ConvertFrom-Json
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ AWS credentials configured successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Account ID: $($newIdentity.Account)" -ForegroundColor Cyan
        Write-Host "User ARN: $($newIdentity.Arn)" -ForegroundColor Cyan
        Write-Host "User ID: $($newIdentity.UserId)" -ForegroundColor Cyan
        
        # Verify it's the correct account
        if ($newIdentity.Account -eq "188238313375") {
            Write-Host ""
            Write-Host "✓ Confirmed: Correct AWS account (188238313375)" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "⚠ Warning: Different AWS account detected" -ForegroundColor Yellow
            Write-Host "  Expected: 188238313375" -ForegroundColor Gray
            Write-Host "  Got: $($newIdentity.Account)" -ForegroundColor Gray
        }
        
    } else {
        Write-Host "✗ Failed to verify credentials" -ForegroundColor Red
        Write-Host "Error: $newIdentity" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Failed to verify credentials" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 5: Test access to key resources
Write-Host "Step 5: Testing access to project resources..." -ForegroundColor Yellow
Write-Host ""

# Test S3 access
Write-Host "Testing S3 access..." -ForegroundColor Cyan
try {
    $s3Test = aws s3 ls s3://ure-mvp-data-us-east-1-188238313375 --region us-east-1 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ S3 bucket access: OK" -ForegroundColor Green
    } else {
        Write-Host "  ✗ S3 bucket access: FAILED" -ForegroundColor Red
    }
} catch {
    Write-Host "  ✗ S3 bucket access: FAILED" -ForegroundColor Red
}

# Test Lambda access
Write-Host "Testing Lambda access..." -ForegroundColor Cyan
try {
    $lambdaTest = aws lambda get-function --function-name ure-mvp-handler-docker --region us-east-1 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Lambda access: OK" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Lambda access: FAILED" -ForegroundColor Red
    }
} catch {
    Write-Host "  ✗ Lambda access: FAILED" -ForegroundColor Red
}

# Test DynamoDB access
Write-Host "Testing DynamoDB access..." -ForegroundColor Cyan
try {
    $dynamoTest = aws dynamodb describe-table --table-name ure-conversations --region us-east-1 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ DynamoDB access: OK" -ForegroundColor Green
    } else {
        Write-Host "  ✗ DynamoDB access: FAILED" -ForegroundColor Red
    }
} catch {
    Write-Host "  ✗ DynamoDB access: FAILED" -ForegroundColor Red
}

# Test ECR access
Write-Host "Testing ECR access..." -ForegroundColor Cyan
try {
    $ecrTest = aws ecr describe-repositories --repository-names ure-lambda --region us-east-1 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ ECR access: OK" -ForegroundColor Green
    } else {
        Write-Host "  ✗ ECR access: FAILED" -ForegroundColor Red
    }
} catch {
    Write-Host "  ✗ ECR access: FAILED" -ForegroundColor Red
}

Write-Host ""

# Step 6: Update .env file if it exists
Write-Host "Step 6: Checking for .env file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  Found .env file" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "⚠ WARNING: If your .env file contains AWS credentials, update them now!" -ForegroundColor Red
    Write-Host "  File location: $(Get-Location)\.env" -ForegroundColor Gray
    Write-Host ""
    $updateEnv = Read-Host "Open .env file for editing? (yes/no)"
    if ($updateEnv -eq "yes") {
        notepad .env
    }
} else {
    Write-Host "  No .env file found (this is OK)" -ForegroundColor Gray
}

Write-Host ""

# Step 7: Delete old access keys
Write-Host "Step 7: Delete old (exposed) access keys" -ForegroundColor Yellow
Write-Host ""
Write-Host "IMPORTANT: You must delete the old exposed access keys!" -ForegroundColor Red
Write-Host ""
Write-Host "Steps to delete old keys:" -ForegroundColor Cyan
Write-Host "  1. Go to: AWS Console → IAM → Users → [Your Username] → Security Credentials" -ForegroundColor Gray
Write-Host "  2. Find the OLD access keys (not the ones you just created)" -ForegroundColor Gray
Write-Host "  3. Click 'Actions' → 'Deactivate' (to test first)" -ForegroundColor Gray
Write-Host "  4. Verify everything still works with new keys" -ForegroundColor Gray
Write-Host "  5. Click 'Actions' → 'Delete' to permanently remove old keys" -ForegroundColor Gray
Write-Host ""

$deletedOld = Read-Host "Have you deleted the old access keys? (yes/no)"
if ($deletedOld -eq "yes") {
    Write-Host "✓ Old keys deleted" -ForegroundColor Green
} else {
    Write-Host "⚠ Remember to delete old keys after verifying new ones work!" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Configuration Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. ✓ New AWS credentials configured" -ForegroundColor Green
Write-Host "  2. ⏳ Remove exposed file from git history (see SECURITY_INCIDENT_RESPONSE.md)" -ForegroundColor Yellow
Write-Host "  3. ⏳ Run security audit to check for unauthorized access" -ForegroundColor Yellow
Write-Host ""
Write-Host "For detailed instructions, see: SECURITY_INCIDENT_RESPONSE.md" -ForegroundColor Gray
