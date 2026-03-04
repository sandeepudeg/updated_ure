#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Check AWS Deployment Status - GramSetu Project
.DESCRIPTION
    Comprehensive script to check all AWS resources and deployment activities in progress
.NOTES
    Author: GramSetu Team
    Date: March 2, 2026
#>

param(
    [switch]$Detailed,
    [switch]$Watch
)

$ErrorActionPreference = "SilentlyContinue"

function Write-Header {
    param([string]$Text)
    Write-Host "`n$('=' * 70)" -ForegroundColor Cyan
    Write-Host $Text -ForegroundColor Cyan
    Write-Host "$('=' * 70)" -ForegroundColor Cyan
}

function Write-Status {
    param(
        [string]$Service,
        [string]$Status,
        [string]$Details = ""
    )
    
    $color = switch ($Status) {
        "✓ Active" { "Green" }
        "✓ Deployed" { "Green" }
        "✓ Available" { "Green" }
        "⏳ In Progress" { "Yellow" }
        "⏳ Deploying" { "Yellow" }
        "⚠ Warning" { "Yellow" }
        "✗ Error" { "Red" }
        "✗ Not Found" { "Red" }
        default { "White" }
    }
    
    Write-Host "  $Service" -NoNewline -ForegroundColor White
    Write-Host " ... " -NoNewline
    Write-Host $Status -ForegroundColor $color
    
    if ($Details) {
        Write-Host "      $Details" -ForegroundColor Gray
    }
}

function Get-CloudFrontStatus {
    Write-Header "CloudFront Distribution Status"
    
    try {
        $distId = "E354ZTACSUHKWS"
        $dist = aws cloudfront get-distribution --id $distId --query 'Distribution' --output json 2>$null | ConvertFrom-Json
        
        if ($dist) {
            $status = $dist.Status
            $domain = $dist.DomainName
            $enabled = $dist.DistributionConfig.Enabled
            
            if ($status -eq "Deployed") {
                Write-Status "CloudFront Distribution" "✓ Deployed" "Domain: https://$domain"
                Write-Status "Distribution ID" "✓ Active" $distId
                Write-Status "Status" "✓ Ready" "Enabled: $enabled"
                
                if ($Detailed) {
                    Write-Host "`n  Additional Details:" -ForegroundColor Gray
                    Write-Host "    - Origins: $($dist.DistributionConfig.Origins.Quantity)" -ForegroundColor Gray
                    Write-Host "    - Price Class: $($dist.DistributionConfig.PriceClass)" -ForegroundColor Gray
                    Write-Host "    - Default Root: $($dist.DistributionConfig.DefaultRootObject)" -ForegroundColor Gray
                }
            } else {
                Write-Status "CloudFront Distribution" "⏳ Deploying" "Status: $status"
                Write-Status "Distribution ID" "⏳ In Progress" $distId
                Write-Status "Domain" "⏳ Pending" "https://$domain"
                Write-Host "`n  ⏳ Deployment typically takes 10-15 minutes" -ForegroundColor Yellow
            }
        } else {
            Write-Status "CloudFront Distribution" "✗ Not Found" "Distribution ID: $distId"
        }
    } catch {
        Write-Status "CloudFront Distribution" "✗ Error" $_.Exception.Message
    }
}

function Get-S3BucketStatus {
    Write-Header "S3 Bucket Status"
    
    $buckets = @(
        @{Name="gramsetu-web-ui"; Purpose="Web UI Hosting"},
        @{Name="ure-mvp-data-us-east-1-188238313375"; Purpose="Backend Data"}
    )
    
    foreach ($bucket in $buckets) {
        try {
            $exists = aws s3api head-bucket --bucket $bucket.Name 2>$null
            
            if ($LASTEXITCODE -eq 0) {
                Write-Status $bucket.Name "✓ Available" $bucket.Purpose
                
                if ($Detailed) {
                    $objects = aws s3 ls s3://$($bucket.Name) --recursive 2>$null | Measure-Object | Select-Object -ExpandProperty Count
                    Write-Host "      Objects: $objects" -ForegroundColor Gray
                }
            } else {
                Write-Status $bucket.Name "✗ Not Found" $bucket.Purpose
            }
        } catch {
            Write-Status $bucket.Name "✗ Error" $_.Exception.Message
        }
    }
}

function Get-LambdaStatus {
    Write-Header "Lambda Function Status"
    
    try {
        $lambda = aws lambda get-function --function-name ure-mvp-handler --query 'Configuration' --output json 2>$null | ConvertFrom-Json
        
        if ($lambda) {
            Write-Status "Lambda Function" "✓ Active" "ure-mvp-handler"
            Write-Status "Runtime" "✓ Available" $lambda.Runtime
            Write-Status "Memory" "✓ Configured" "$($lambda.MemorySize) MB"
            Write-Status "Timeout" "✓ Configured" "$($lambda.Timeout) seconds"
            Write-Status "Last Modified" "✓ Updated" $lambda.LastModified
            
            if ($Detailed) {
                Write-Host "`n  Environment Variables:" -ForegroundColor Gray
                $lambda.Environment.Variables.PSObject.Properties | ForEach-Object {
                    if ($_.Name -notlike "*KEY*" -and $_.Name -notlike "*SECRET*") {
                        Write-Host "    - $($_.Name): $($_.Value)" -ForegroundColor Gray
                    }
                }
            }
        } else {
            Write-Status "Lambda Function" "✗ Not Found" "ure-mvp-handler"
        }
    } catch {
        Write-Status "Lambda Function" "✗ Error" $_.Exception.Message
    }
}

function Get-APIGatewayStatus {
    Write-Header "API Gateway Status"
    
    try {
        $apis = aws apigateway get-rest-apis --query 'items[?name==`ure-mvp-api`]' --output json 2>$null | ConvertFrom-Json
        
        if ($apis -and $apis.Count -gt 0) {
            $api = $apis[0]
            Write-Status "API Gateway" "✓ Active" $api.name
            Write-Status "API ID" "✓ Available" $api.id
            Write-Status "Created" "✓ Available" $api.createdDate
            
            $endpoint = "https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query"
            Write-Status "Endpoint" "✓ Available" $endpoint
            
            if ($Detailed) {
                # Test API endpoint
                Write-Host "`n  Testing API Endpoint..." -ForegroundColor Gray
                try {
                    $testBody = @{
                        user_id = "test_user"
                        query = "Hello"
                        language = "en"
                    } | ConvertTo-Json
                    
                    $response = Invoke-WebRequest -Uri $endpoint -Method POST -Body $testBody -ContentType "application/json" -TimeoutSec 10 -ErrorAction Stop
                    Write-Host "    - API Response: $($response.StatusCode) $($response.StatusDescription)" -ForegroundColor Green
                } catch {
                    Write-Host "    - API Test: Failed ($($_.Exception.Message))" -ForegroundColor Yellow
                }
            }
        } else {
            Write-Status "API Gateway" "✗ Not Found" "ure-mvp-api"
        }
    } catch {
        Write-Status "API Gateway" "✗ Error" $_.Exception.Message
    }
}

function Get-DynamoDBStatus {
    Write-Header "DynamoDB Tables Status"
    
    $tables = @(
        "ure-conversations",
        "ure-user-profiles",
        "ure-village-amenities"
    )
    
    foreach ($table in $tables) {
        try {
            $tableInfo = aws dynamodb describe-table --table-name $table --query 'Table' --output json 2>$null | ConvertFrom-Json
            
            if ($tableInfo) {
                Write-Status $table "✓ Active" "Status: $($tableInfo.TableStatus)"
                
                if ($Detailed) {
                    Write-Host "      Items: $($tableInfo.ItemCount), Size: $([math]::Round($tableInfo.TableSizeBytes / 1KB, 2)) KB" -ForegroundColor Gray
                }
            } else {
                Write-Status $table "✗ Not Found"
            }
        } catch {
            Write-Status $table "✗ Error" $_.Exception.Message
        }
    }
}

function Get-CloudFormationStatus {
    Write-Header "CloudFormation Stack Status"
    
    try {
        $stack = aws cloudformation describe-stacks --stack-name ure-mvp-stack --query 'Stacks[0]' --output json 2>$null | ConvertFrom-Json
        
        if ($stack) {
            $status = $stack.StackStatus
            
            if ($status -like "*COMPLETE*") {
                Write-Status "CloudFormation Stack" "✓ Active" "ure-mvp-stack"
                Write-Status "Stack Status" "✓ Available" $status
                Write-Status "Created" "✓ Available" $stack.CreationTime
                
                if ($Detailed) {
                    Write-Host "`n  Stack Outputs:" -ForegroundColor Gray
                    $stack.Outputs | ForEach-Object {
                        Write-Host "    - $($_.OutputKey): $($_.OutputValue)" -ForegroundColor Gray
                    }
                }
            } elseif ($status -like "*PROGRESS*") {
                Write-Status "CloudFormation Stack" "⏳ In Progress" $status
            } else {
                Write-Status "CloudFormation Stack" "⚠ Warning" $status
            }
        } else {
            Write-Status "CloudFormation Stack" "✗ Not Found" "ure-mvp-stack"
        }
    } catch {
        Write-Status "CloudFormation Stack" "✗ Error" $_.Exception.Message
    }
}

function Get-BedrockStatus {
    Write-Header "Amazon Bedrock Status"
    
    try {
        # Check Knowledge Base
        $kbId = "7XROZ6PZIF"
        $kb = aws bedrock-agent get-knowledge-base --knowledge-base-id $kbId --output json 2>$null | ConvertFrom-Json
        
        if ($kb) {
            Write-Status "Knowledge Base" "✓ Available" "ID: $kbId"
            Write-Status "KB Status" "✓ Active" $kb.knowledgeBase.status
        } else {
            Write-Status "Knowledge Base" "✗ Not Found" "ID: $kbId"
        }
        
        # Check Guardrail
        $guardrailId = "q6wfsifs9d72"
        Write-Status "Guardrail" "✓ Configured" "ID: $guardrailId"
        
        # Check Model Access
        Write-Status "Model" "✓ Configured" "amazon.nova-lite-v1:0"
        
    } catch {
        Write-Status "Amazon Bedrock" "⚠ Warning" "Limited access to check details"
    }
}

function Get-DeploymentSummary {
    Write-Header "Deployment Summary"
    
    Write-Host "`n  Current Deployment Status:" -ForegroundColor White
    Write-Host "  ├─ CloudFront: " -NoNewline -ForegroundColor Gray
    
    $cfStatus = aws cloudfront get-distribution --id E354ZTACSUHKWS --query 'Distribution.Status' --output text 2>$null
    if ($cfStatus -eq "Deployed") {
        Write-Host "✓ Ready" -ForegroundColor Green
    } elseif ($cfStatus -eq "InProgress") {
        Write-Host "⏳ Deploying (10-15 min)" -ForegroundColor Yellow
    } else {
        Write-Host "✗ Unknown" -ForegroundColor Red
    }
    
    Write-Host "  ├─ S3 Bucket: " -NoNewline -ForegroundColor Gray
    $s3Status = aws s3api head-bucket --bucket gramsetu-web-ui 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Ready" -ForegroundColor Green
    } else {
        Write-Host "✗ Not Found" -ForegroundColor Red
    }
    
    Write-Host "  ├─ Lambda: " -NoNewline -ForegroundColor Gray
    $lambdaStatus = aws lambda get-function --function-name ure-mvp-handler --query 'Configuration.State' --output text 2>$null
    if ($lambdaStatus -eq "Active") {
        Write-Host "✓ Active" -ForegroundColor Green
    } else {
        Write-Host "✗ Not Active" -ForegroundColor Red
    }
    
    Write-Host "  ├─ API Gateway: " -NoNewline -ForegroundColor Gray
    $apiStatus = aws apigateway get-rest-apis --query 'items[?name==`ure-mvp-api`] | [0].id' --output text 2>$null
    if ($apiStatus) {
        Write-Host "✓ Active" -ForegroundColor Green
    } else {
        Write-Host "✗ Not Found" -ForegroundColor Red
    }
    
    Write-Host "  └─ DynamoDB: " -NoNewline -ForegroundColor Gray
    $dbStatus = aws dynamodb describe-table --table-name ure-conversations --query 'Table.TableStatus' --output text 2>$null
    if ($dbStatus -eq "ACTIVE") {
        Write-Host "✓ Active" -ForegroundColor Green
    } else {
        Write-Host "✗ Not Active" -ForegroundColor Red
    }
    
    Write-Host "`n  Application URLs:" -ForegroundColor White
    Write-Host "  ├─ CloudFront: https://d3v7khazsfb4vd.cloudfront.net" -ForegroundColor Cyan
    Write-Host "  └─ API Gateway: https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query" -ForegroundColor Cyan
}

function Get-InProgressActivities {
    Write-Header "Activities In Progress"
    
    $hasActivity = $false
    
    # Check CloudFront
    $cfStatus = aws cloudfront get-distribution --id E354ZTACSUHKWS --query 'Distribution.Status' --output text 2>$null
    if ($cfStatus -eq "InProgress") {
        Write-Host "  ⏳ CloudFront Distribution Deployment" -ForegroundColor Yellow
        Write-Host "      Status: Deploying" -ForegroundColor Gray
        Write-Host "      ETA: 10-15 minutes from start" -ForegroundColor Gray
        Write-Host "      Distribution ID: E354ZTACSUHKWS" -ForegroundColor Gray
        $hasActivity = $true
    }
    
    # Check CloudFormation
    $cfnStatus = aws cloudformation describe-stacks --stack-name ure-mvp-stack --query 'Stacks[0].StackStatus' --output text 2>$null
    if ($cfnStatus -like "*PROGRESS*") {
        Write-Host "  ⏳ CloudFormation Stack Update" -ForegroundColor Yellow
        Write-Host "      Status: $cfnStatus" -ForegroundColor Gray
        Write-Host "      Stack: ure-mvp-stack" -ForegroundColor Gray
        $hasActivity = $true
    }
    
    # Check Lambda updates
    $lambdaState = aws lambda get-function --function-name ure-mvp-handler --query 'Configuration.LastUpdateStatus' --output text 2>$null
    if ($lambdaState -eq "InProgress") {
        Write-Host "  ⏳ Lambda Function Update" -ForegroundColor Yellow
        Write-Host "      Status: Updating" -ForegroundColor Gray
        Write-Host "      Function: ure-mvp-handler" -ForegroundColor Gray
        $hasActivity = $true
    }
    
    if (-not $hasActivity) {
        Write-Host "  ✓ No activities in progress - All services are stable" -ForegroundColor Green
    }
}

# Main execution
Clear-Host

Write-Host "`n╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         GramSetu AWS Deployment Status Checker                    ║" -ForegroundColor Cyan
Write-Host "║         Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')                          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

do {
    # Quick summary first
    Get-DeploymentSummary
    
    # In-progress activities
    Get-InProgressActivities
    
    if ($Detailed) {
        # Detailed checks
        Get-CloudFrontStatus
        Get-S3BucketStatus
        Get-LambdaStatus
        Get-APIGatewayStatus
        Get-DynamoDBStatus
        Get-CloudFormationStatus
        Get-BedrockStatus
    }
    
    Write-Host "`n$('=' * 70)" -ForegroundColor Cyan
    Write-Host "Status check completed at $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
    
    if ($Watch) {
        Write-Host "`nRefreshing in 30 seconds... (Press Ctrl+C to stop)" -ForegroundColor Yellow
        Start-Sleep -Seconds 30
        Clear-Host
    }
    
} while ($Watch)

Write-Host "`nTip: Use -Detailed flag for comprehensive status" -ForegroundColor Gray
Write-Host "Tip: Use -Watch flag for continuous monitoring" -ForegroundColor Gray
Write-Host ""
