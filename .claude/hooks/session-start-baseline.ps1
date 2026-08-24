#requires -Version 5.1
# Capture a baseline of FrameworX process families at session start.
# Paired with session-stop-reap.ps1: at session end, only processes that are NOT in
# this baseline AND started after it are treated as session-spawned orphans.
# The operator's pre-existing Designer / TServer processes are never touched.

$ErrorActionPreference = 'SilentlyContinue'

try {
    $raw = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($raw)) { exit 0 }
    $payload = $raw | ConvertFrom-Json
} catch {
    exit 0
}

$sessionId = $payload.session_id
if ([string]::IsNullOrWhiteSpace($sessionId)) { exit 0 }

$baselineDir = Join-Path $env:TEMP 'claude-orphan-baselines'
if (-not (Test-Path $baselineDir)) {
    New-Item -ItemType Directory -Path $baselineDir -Force | Out-Null
}
$baselineFile = Join-Path $baselineDir "$sessionId.json"

$procs = Get-Process Designer, TServer, TRunModule, TStartup -ErrorAction SilentlyContinue |
    ForEach-Object {
        $start = $null
        try { $start = $_.StartTime.ToString('o') } catch {}
        [PSCustomObject]@{
            Id          = $_.Id
            ProcessName = $_.ProcessName
            StartTime   = $start
        }
    }

$baseline = [PSCustomObject]@{
    sessionId   = $sessionId
    cwd         = $payload.cwd
    capturedAt  = (Get-Date).ToString('o')
    processes   = @($procs)
}

$baseline | ConvertTo-Json -Depth 5 | Out-File -FilePath $baselineFile -Encoding utf8
exit 0
