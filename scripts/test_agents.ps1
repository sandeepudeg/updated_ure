# GramSetu Agent Testing Script (PowerShell)
# Tests all 6 agents with various queries to validate functionality

param(
    [string]$ApiEndpoint = "https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query",
    [string]$UserId = "test_farmer_gramsetu",
    [string]$Location = "Nashik, Maharashtra",
    [switch]$Verbose
)

Write-Host "`n################################################################################" -ForegroundColor Cyan
Write-Host "# GramSetu Agent Testing Suite" -ForegroundColor Cyan
Write-Host "# Started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "# API Endpoint: $ApiEndpoint" -ForegroundColor Cyan
Write-Host "# Test User: $UserId" -ForegroundColor Cyan
Write-Host "# Location: $Location" -ForegroundColor Cyan
Write-Host "################################################################################`n" -ForegroundColor Cyan

# Test queries for each agent
$testQueries = @{
    'krishak-mitra' = @(
        @{
            query = 'What is the best time to plant wheat in Maharashtra?'
            description = 'Crop timing advice'
            expectedKeywords = @('wheat', 'plant', 'season', 'Maharashtra')
        },
        @{
            query = 'How much water does rice crop need per day?'
            description = 'Irrigation requirements'
            expectedKeywords = @('rice', 'water', 'irrigation')
        },
        @{
            query = 'What are the best organic fertilizers for tomato plants?'
            description = 'Fertilizer recommendations'
            expectedKeywords = @('organic', 'fertilizer', 'tomato')
        }
    )
    'rog-nivaarak' = @(
        @{
            query = 'My tomato leaves have brown spots. What disease is this?'
            description = 'Disease identification'
            expectedKeywords = @('disease', 'tomato', 'leaf', 'spot')
        },
        @{
            query = 'How to treat powdery mildew on grapes organically?'
            description = 'Organic treatment'
            expectedKeywords = @('powdery mildew', 'grape', 'organic', 'treatment')
        },
        @{
            query = 'What are common pests affecting cotton crops?'
            description = 'Pest identification'
            expectedKeywords = @('pest', 'cotton', 'insect')
        }
    )
    'bazaar-darshi' = @(
        @{
            query = 'What is the current market price of onions in Nashik?'
            description = 'Market price query'
            expectedKeywords = @('price', 'onion', 'market', 'Nashik')
        },
        @{
            query = 'Which crops have the best profit margins this season?'
            description = 'Profit analysis'
            expectedKeywords = @('profit', 'crop', 'margin', 'season')
        },
        @{
            query = 'Where can I sell my wheat harvest for the best price?'
            description = 'Market connection'
            expectedKeywords = @('sell', 'wheat', 'price', 'market')
        }
    )
    'sarkar-sahayak' = @(
        @{
            query = 'What is PM-KISAN scheme and am I eligible?'
            description = 'Scheme information'
            expectedKeywords = @('PM-KISAN', 'scheme', 'eligible', 'benefit')
        },
        @{
            query = 'How to apply for crop insurance under PMFBY?'
            description = 'Application process'
            expectedKeywords = @('PMFBY', 'insurance', 'apply', 'crop')
        },
        @{
            query = 'What subsidies are available for drip irrigation?'
            description = 'Subsidy information'
            expectedKeywords = @('subsidy', 'drip', 'irrigation', 'scheme')
        }
    )
    'mausam-gyaata' = @(
        @{
            query = 'What is the weather forecast for Nashik this week?'
            description = 'Weather forecast'
            expectedKeywords = @('weather', 'forecast', 'Nashik', 'week')
        },
        @{
            query = 'When should I irrigate my crops based on upcoming weather?'
            description = 'Irrigation timing'
            expectedKeywords = @('irrigate', 'weather', 'crop', 'water')
        },
        @{
            query = 'Is there a risk of frost in the next few days?'
            description = 'Weather alert'
            expectedKeywords = @('frost', 'temperature', 'risk', 'cold')
        }
    )
    'krishi-bodh' = @(
        @{
            query = 'What are the latest farming techniques for water conservation?'
            description = 'Modern techniques'
            expectedKeywords = @('technique', 'water', 'conservation', 'farming')
        },
        @{
            query = 'How can I improve soil health organically?'
            description = 'Soil management'
            expectedKeywords = @('soil', 'health', 'organic', 'improve')
        },
        @{
            query = 'What training programs are available for farmers?'
            description = 'Educational resources'
            expectedKeywords = @('training', 'program', 'farmer', 'education')
        }
    )
}

# Results tracking
$allResults = @{
    agents = @{}
    summary = @{
        totalTests = 0
        totalPassed = 0
        totalFailed = 0
    }
}

# Function to send query to API
function Send-Query {
    param(
        [string]$Query,
        [string]$Language = 'en'
    )
    
    $payload = @{
        user_id = $UserId
        query = $Query
        language = $Language
        location = $Location
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri $ApiEndpoint -Method Post -Body $payload -ContentType 'application/json' -TimeoutSec 30
        return $response
    }
    catch {
        return @{
            error = $_.Exception.Message
            success = $false
        }
    }
}

# Function to validate response
function Test-Response {
    param(
        [object]$Response,
        [array]$ExpectedKeywords
    )
    
    if ($Response.error) {
        return @{
            valid = $false
            reason = "API Error: $($Response.error)"
            keywordsFound = @()
        }
    }
    
    $responseText = $Response.response.ToLower()
    $keywordsFound = $ExpectedKeywords | Where-Object { $responseText -like "*$($_.ToLower())*" }
    
    return @{
        valid = $keywordsFound.Count -gt 0
        keywordsFound = $keywordsFound
        keywordsMissing = $ExpectedKeywords | Where-Object { $_ -notin $keywordsFound }
        responseLength = $responseText.Length
    }
}

# Test each agent
foreach ($agentName in $testQueries.Keys) {
    Write-Host "`n================================================================================" -ForegroundColor Yellow
    Write-Host "Testing Agent: $($agentName.ToUpper())" -ForegroundColor Yellow
    Write-Host "================================================================================`n" -ForegroundColor Yellow
    
    $agentResults = @{
        agentName = $agentName
        totalTests = $testQueries[$agentName].Count
        passed = 0
        failed = 0
        testCases = @()
    }
    
    $testNumber = 1
    foreach ($testCase in $testQueries[$agentName]) {
        Write-Host "Test $testNumber/$($agentResults.totalTests): $($testCase.description)" -ForegroundColor Cyan
        Write-Host "Query: $($testCase.query)" -ForegroundColor Gray
        
        $startTime = Get-Date
        $response = Send-Query -Query $testCase.query
        $responseTime = ((Get-Date) - $startTime).TotalSeconds
        
        $validation = Test-Response -Response $response -ExpectedKeywords $testCase.expectedKeywords
        
        $testResult = @{
            testNumber = $testNumber
            description = $testCase.description
            query = $testCase.query
            responseTime = [math]::Round($responseTime, 2)
            success = -not $response.error
            validation = $validation
            agentUsed = $response.agent_used
            responsePreview = if ($response.response) { $response.response.Substring(0, [Math]::Min(200, $response.response.Length)) + "..." } else { $null }
        }
        
        if ($testResult.success -and $validation.valid) {
            $agentResults.passed++
            Write-Host "✅ PASSED (Response time: $($responseTime.ToString('F2'))s)" -ForegroundColor Green
            Write-Host "   Agent used: $($testResult.agentUsed)" -ForegroundColor Gray
            Write-Host "   Keywords found: $($validation.keywordsFound -join ', ')" -ForegroundColor Gray
        }
        else {
            $agentResults.failed++
            Write-Host "❌ FAILED" -ForegroundColor Red
            if (-not $testResult.success) {
                Write-Host "   Error: $($response.error)" -ForegroundColor Red
            }
            else {
                Write-Host "   Validation failed: No expected keywords found" -ForegroundColor Red
                Write-Host "   Keywords missing: $($validation.keywordsMissing -join ', ')" -ForegroundColor Red
            }
        }
        
        if ($testResult.responsePreview) {
            Write-Host "   Response preview: $($testResult.responsePreview)" -ForegroundColor Gray
        }
        
        $agentResults.testCases += $testResult
        $testNumber++
        
        # Rate limiting
        Start-Sleep -Seconds 1
    }
    
    $allResults.agents[$agentName] = $agentResults
    $allResults.summary.totalTests += $agentResults.totalTests
    $allResults.summary.totalPassed += $agentResults.passed
    $allResults.summary.totalFailed += $agentResults.failed
}

# Test multilingual support
Write-Host "`n================================================================================" -ForegroundColor Yellow
Write-Host "Testing Multilingual Support" -ForegroundColor Yellow
Write-Host "================================================================================`n" -ForegroundColor Yellow

$testLanguages = @(
    @{ code = 'hi'; name = 'हिंदी'; query = 'What is the best fertilizer for wheat?' },
    @{ code = 'mr'; name = 'मराठी'; query = 'What is the weather forecast for today?' },
    @{ code = 'en'; name = 'English'; query = 'How to control pests in cotton?' }
)

$multilingualResults = @{
    totalLanguages = $testLanguages.Count
    passed = 0
    failed = 0
    results = @()
}

foreach ($lang in $testLanguages) {
    Write-Host "`nTesting $($lang.name) ($($lang.code))" -ForegroundColor Cyan
    Write-Host "Query: $($lang.query)" -ForegroundColor Gray
    
    $startTime = Get-Date
    $response = Send-Query -Query $lang.query -Language $lang.code
    $responseTime = ((Get-Date) - $startTime).TotalSeconds
    
    $result = @{
        language = $lang.name
        languageCode = $lang.code
        success = -not $response.error
        responseTime = [math]::Round($responseTime, 2)
        translated = $response.metadata.translated
        responsePreview = if ($response.response) { $response.response.Substring(0, [Math]::Min(200, $response.response.Length)) + "..." } else { $null }
    }
    
    if ($result.success) {
        $multilingualResults.passed++
        Write-Host "✅ $($lang.name) test passed (Response time: $($responseTime.ToString('F2'))s)" -ForegroundColor Green
        Write-Host "   Translated: $($result.translated)" -ForegroundColor Gray
        if ($result.responsePreview) {
            Write-Host "   Response preview: $($result.responsePreview)" -ForegroundColor Gray
        }
    }
    else {
        $multilingualResults.failed++
        Write-Host "❌ $($lang.name) test failed" -ForegroundColor Red
        Write-Host "   Error: $($response.error)" -ForegroundColor Red
    }
    
    $multilingualResults.results += $result
    Start-Sleep -Seconds 1
}

$allResults.multilingual = $multilingualResults

# Calculate success rates
$successRate = if ($allResults.summary.totalTests -gt 0) {
    [math]::Round(($allResults.summary.totalPassed / $allResults.summary.totalTests * 100), 2)
} else { 0 }

$multilingualSuccessRate = if ($multilingualResults.totalLanguages -gt 0) {
    [math]::Round(($multilingualResults.passed / $multilingualResults.totalLanguages * 100), 2)
} else { 0 }

# Print summary
Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "================================================================================`n" -ForegroundColor Cyan

Write-Host "Agent Tests:" -ForegroundColor White
Write-Host "  Total Agents Tested: $($testQueries.Keys.Count)" -ForegroundColor Gray
Write-Host "  Total Test Cases: $($allResults.summary.totalTests)" -ForegroundColor Gray
Write-Host "  Passed: $($allResults.summary.totalPassed) ✅" -ForegroundColor Green
Write-Host "  Failed: $($allResults.summary.totalFailed) ❌" -ForegroundColor Red
Write-Host "  Success Rate: $successRate%" -ForegroundColor $(if ($successRate -ge 80) { 'Green' } else { 'Yellow' })

Write-Host "`nAgent Breakdown:" -ForegroundColor White
foreach ($agentName in $allResults.agents.Keys) {
    $agent = $allResults.agents[$agentName]
    $status = if ($agent.failed -eq 0) { "✅" } else { "⚠️" }
    Write-Host "  $status $agentName`: $($agent.passed)/$($agent.totalTests) passed" -ForegroundColor Gray
}

Write-Host "`nMultilingual Support:" -ForegroundColor White
Write-Host "  Success Rate: $multilingualSuccessRate%" -ForegroundColor $(if ($multilingualSuccessRate -ge 80) { 'Green' } else { 'Yellow' })

Write-Host "`n================================================================================`n" -ForegroundColor Cyan

# Save results to JSON file
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$outputFile = "test_results_$timestamp.json"
$allResults | ConvertTo-Json -Depth 10 | Out-File -FilePath $outputFile -Encoding UTF8

Write-Host "📄 Full results saved to: $outputFile" -ForegroundColor Cyan

# Exit with appropriate code
if ($allResults.summary.totalFailed -eq 0 -and $multilingualResults.failed -eq 0) {
    Write-Host "`n🎉 All tests passed!" -ForegroundColor Green
    exit 0
}
else {
    Write-Host "`n⚠️  Some tests failed. Check the results above." -ForegroundColor Yellow
    exit 1
}
