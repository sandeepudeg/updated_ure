# Simple Security Remediation Script
# Alternative approach using BFG Repo-Cleaner or manual git commands

Write-Host "=== AWS Credential Exposure Remediation (Simple Method) ===" -ForegroundColor Red
Write-Host ""

# Step 1: Ensure file is deleted and in .gitignore
Write-Host "Step 1: Verifying file deletion and .gitignore..." -ForegroundColor Yellow

if (Test-Path "privacy_audit_report_20260304_155121.json") {
    Remove-Item "privacy_audit_report_20260304_155121.json" -Force
    Write-Host "✓ Deleted file from working directory" -ForegroundColor Green
} else {
    Write-Host "✓ File already deleted from working directory" -ForegroundColor Green
}

# Check .gitignore
$gitignoreContent = Get-Content ".gitignore" -Raw
if ($gitignoreContent -match "report_\*\.json") {
    Write-Host "✓ Pattern already in .gitignore" -ForegroundColor Green
} else {
    Write-Host "⚠ Adding pattern to .gitignore..." -ForegroundColor Yellow
    Add-Content ".gitignore" "`n# Privacy audit reports (may contain sensitive data)`nprivacy_audit_report_*.json`nreport_*.json"
    Write-Host "✓ Added to .gitignore" -ForegroundColor Green
}

Write-Host ""

# Step 2: Commit the removal
Write-Host "Step 2: Committing file removal..." -ForegroundColor Yellow
git rm --cached privacy_audit_report_20260304_155121.json 2>$null
git add .gitignore
git commit -m "Security: Remove exposed AWS credentials and update .gitignore"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Committed removal" -ForegroundColor Green
} else {
    Write-Host "⚠ Nothing to commit (file may already be removed)" -ForegroundColor Yellow
}

Write-Host ""

# Step 3: Create a new commit to overwrite history
Write-Host "Step 3: Pushing changes..." -ForegroundColor Yellow
git push origin main

Write-Host ""
Write-Host "=== IMPORTANT: History Still Contains Credentials ===" -ForegroundColor Red
Write-Host ""
Write-Host "The file is still in git history at commit 3642b7cd." -ForegroundColor Yellow
Write-Host "To completely remove it, you have two options:" -ForegroundColor Yellow
Write-Host ""
Write-Host "OPTION 1: Use BFG Repo-Cleaner (Recommended)" -ForegroundColor Cyan
Write-Host "  1. Download BFG: https://rtyley.github.io/bfg-repo-cleaner/" -ForegroundColor Gray
Write-Host "  2. Run: java -jar bfg.jar --delete-files privacy_audit_report_20260304_155121.json" -ForegroundColor Gray
Write-Host "  3. Run: git reflog expire --expire=now --all && git gc --prune=now --aggressive" -ForegroundColor Gray
Write-Host "  4. Run: git push origin --force --all" -ForegroundColor Gray
Write-Host ""
Write-Host "OPTION 2: Use git-filter-repo" -ForegroundColor Cyan
Write-Host "  1. Install: pip install git-filter-repo" -ForegroundColor Gray
Write-Host "  2. Run: git filter-repo --path privacy_audit_report_20260304_155121.json --invert-paths --force" -ForegroundColor Gray
Write-Host "  3. Run: git push origin --force --all" -ForegroundColor Gray
Write-Host ""
Write-Host "=== CRITICAL: ROTATE AWS CREDENTIALS NOW ===" -ForegroundColor Red
Write-Host ""
Write-Host "1. Go to AWS Console → IAM → Users → Security Credentials" -ForegroundColor Yellow
Write-Host "2. Deactivate and DELETE the exposed access keys" -ForegroundColor Yellow
Write-Host "3. Create NEW access keys" -ForegroundColor Yellow
Write-Host "4. Update ~/.aws/credentials with new keys" -ForegroundColor Yellow
Write-Host ""
Write-Host "The exposed credentials are TEMPORARY ACCESS KEYS from STS." -ForegroundColor Cyan
Write-Host "They may have already expired, but you should still:" -ForegroundColor Cyan
Write-Host "  - Check CloudTrail for unauthorized access" -ForegroundColor Gray
Write-Host "  - Review IAM activity logs" -ForegroundColor Gray
Write-Host "  - Verify no unexpected resources were created" -ForegroundColor Gray
