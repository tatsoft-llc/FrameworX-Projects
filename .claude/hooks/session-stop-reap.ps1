#requires -Version 5.1
# Session hygiene: close out the FrameworX processes this session started and left running.
# Paired with session-start-baseline.ps1.
#
# Safety: only stops processes whose PID is NOT in the baseline AND whose StartTime
# is after the baseline capture. The operator's pre-existing Designer.exe / TServer.exe
# (ones already running before the Claude session started) are NEVER touched.
# For the mid-session case (blocked right now on a .dbsln or bridge port still held by
# an earlier process), use the kill-zombies skill instead: this hook only runs at session end.
# (kill-zombies ships in the companion repo: github.com/tatsoft-llc/Claude-Code-Skills)

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
$baselineFile = Join-Path $baselineDir "$sessionId.json"
if (-not (Test-Path $baselineFile)) {
    # No baseline captured - cannot safely distinguish orphan from pre-existing. Bail clean.
    exit 0
}

$baseline = Get-Content $baselineFile -Raw | ConvertFrom-Json
$baselinePids = @{}
foreach ($p in $baseline.processes) { $baselinePids[[int]$p.Id] = $true }

try { $baselineCutoff = [datetime]::Parse($baseline.capturedAt) } catch { $baselineCutoff = [datetime]::MinValue }

$current = Get-Process Designer, TServer, TRunModule, TStartup -ErrorAction SilentlyContinue
$orphans = @()
foreach ($proc in $current) {
    if ($baselinePids.ContainsKey([int]$proc.Id)) { continue }
    $started = $null
    try { $started = $proc.StartTime } catch {}
    if ($started -and $started -gt $baselineCutoff) {
        $orphans += $proc
    }
}

if (-not $orphans -or $orphans.Count -eq 0) {
    Remove-Item $baselineFile -ErrorAction SilentlyContinue
    exit 0
}

# Log orphans to the workspace's AISessions directory before reaping.
$cwd = $payload.cwd
$date = Get-Date -Format 'yyyy-MM-dd'
$logDir = Join-Path $cwd 'AISessions'
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force -ErrorAction SilentlyContinue | Out-Null }
if (Test-Path $logDir) {
    $logFile = Join-Path $logDir "Orphan-Cleanup-$date.md"
    $now = (Get-Date).ToString('o')
    $lines = @()
    if (-not (Test-Path $logFile)) {
        $lines += "# Orphan cleanup log - $date"
        $lines += ''
    }
    $lines += "## Session $sessionId stop @ $now"
    $lines += "Baseline captured: $($baseline.capturedAt)"
    $lines += "Reaped $($orphans.Count) orphan(s):"
    foreach ($o in $orphans) {
        $started = '?'
        try { $started = $o.StartTime.ToString('o') } catch {}
        $lines += "- $($o.ProcessName) PID=$($o.Id) started=$started"
    }
    $lines += ''
    Add-Content -Path $logFile -Value ($lines -join "`n")
}

foreach ($o in $orphans) {
    try { Stop-Process -Id $o.Id -Force -ErrorAction SilentlyContinue } catch {}
}

Remove-Item $baselineFile -ErrorAction SilentlyContinue
exit 0
