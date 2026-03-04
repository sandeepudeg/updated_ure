# Security Remediation Script
# This script removes exposed AWS credentials from git history

Write-Host "=== AWS Credential Exposure Remediation ===" -ForegroundColor Red
Write-Host ""

# Step 1: Verify git-filter-repo is installed
Write-Host "Step 1: Checking for git-filter-repo..." -ForegroundColor Yellow
$filterRepoInstalled = $false
try {
    git filter-repo --version 2>&1 | Out-Null
    $filterRepoInstalled = $true
    Write-Host "✓ git-filter-repo is installed" -ForegroundColor Green
} catch {
    Write-Host "✗ git-filter-repo is NOT installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install git-filter-repo first:" -ForegroundColor Yellow
    Write-Host "  pip install git-filter-repo" -ForegroundColor Cyan
    Write-Host "  OR" -ForegroundColor Yellow
    Write-Host "  Download from: https://github.com/newren/git-filter-repo" -ForegroundColor Cyan
    exit 1
}

Write-Host ""

# Step 2: Create backup
Write-Host "Step 2: Creating backup..." -ForegroundColor Yellow
$backupDir = ".git-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
Copy-Item -Path ".git" -Destination $backupDir -Recurse -Force
Write-Host "✓ Backup created at: $backupDir" -ForegroundColor Green
Write-Host ""

# Step 3: Remove the exposed file from history
Write-Host "Step 3: Removing exposed file from git history..." -ForegroundColor Yellow
Write-Host "  File: privacy_audit_report_20260304_155121.json" -ForegroundColor Cyan

# Use git-filter-repo to remove the file
git filter-repo --path privacy_audit_report_20260304_155121.json --invert-paths --force

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ File removed from git history" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to remove file from history" -ForegroundColor Red
    Write-Host "  Restoring from backup..." -ForegroundColor Yellow
    Remove-Item -Path ".git" -Recurse -Force
    Copy-Item -Path $backupDir -Destination ".git" -Recurse -Force
    exit 1
}

Write-Host ""

# Step 4: Force push to remote
Write-Host "Step 4: Force pushing to remote..." -ForegroundColor Yellow
Write-Host "  WARNING: This will rewrite remote history!" -ForegroundColor Red
Write-Host ""
$confirm = Read-Host "Type 'YES' to continue with force push"

if ($confirm -eq "YES") {
    git remote add origin-temp $(git remote get-url origin) 2>$null
    git push origin --force --all
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Successfully force pushed to remote" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to force push" -ForegroundColor Red
        Write-Host "  You may need to manually push: git push origin --force --all" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠ Skipped force push. You must manually push:" -ForegroundColor Yellow
    Write-Host "  git push origin --force --all" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=== CRITICAL NEXT STEPS ===" -ForegroundColor Red
Write-Host ""
Write-Host "1. ROTATE AWS CREDENTIALS IMMEDIATELY:" -ForegroundColor Yellow
Write-Host "   - Go to AWS Console → IAM → Users → Your User → Security Credentials" -ForegroundColor Cyan
Write-Host "   - Deactivate and delete the exposed access keys" -ForegroundColor Cyan
Write-Host "   - Create new access keys" -ForegroundColor Cyan
Write-Host "   - Update your local ~/.aws/credentials file" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. VERIFY CLEANUP:" -ForegroundColor Yellow
Write-Host "   git log --all --full-history -- '*report_20260304_155121.json'" -ForegroundColor Cyan
Write-Host "   (Should return no results)" -ForegroundColor Gray
Write-Host ""
Write-Host "3. MONITOR AWS ACCOUNT:" -ForegroundColor Yellow
Write-Host "   - Check CloudTrail for any unauthorized access" -ForegroundColor Cyan
Write-Host "   - Review recent IAM activity" -ForegroundColor Cyan
Write-Host "   - Check for unexpected resource creation" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backup location: $backupDir" -ForegroundColor Gray
Write-Host "You can delete the backup after verifying everything works correctly." -ForegroundColor Gray
