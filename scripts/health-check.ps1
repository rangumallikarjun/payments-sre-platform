<#
.SYNOPSIS
    Quick health-check sweep across all services (PowerShell equivalent of
    health-check.sh). Exits non-zero if any service fails its /healthz or
    /readyz check.
#>

$Services = @{
    "payment-service"      = "http://localhost:8001"
    "fraud-monitor"        = "http://localhost:8002"
    "notification-service" = "http://localhost:8003"
}

$failures = 0

foreach ($name in $Services.Keys) {
    $baseUrl = $Services[$name]
    foreach ($path in @("healthz", "readyz")) {
        $url = "$baseUrl/$path"
        try {
            $response = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Host "OK    $name /$path"
            } else {
                Write-Host "FAIL  $name /$path (status $($response.StatusCode))"
                $failures++
            }
        } catch {
            Write-Host "FAIL  $name /$path ($($_.Exception.Message))"
            $failures++
        }
    }
}

if ($failures -gt 0) {
    Write-Host "$failures check(s) failed"
    exit 1
}

Write-Host "All services healthy"
