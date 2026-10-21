#requires -Version 5.1
# Session hygiene: close out the FrameworX processes this session started and left running.
# Two hook events call this file; session-start-baseline.ps1 runs first:
#   SessionStart  session-start-baseline.ps1         snapshot of the FrameworX processes already running.
#   Stop          session-stop-reap.ps1 -Mode Record after EVERY reply: write down the processes this
#                                                    session started since the snapshot. Stops nothing.
#   SessionEnd    session-stop-reap.ps1 -Mode Reap   when the session closes: stop the recorded
#                                                    processes that are still running.
# Claude Code's Stop event fires at the end of each reply, not when the session closes, so all
# stopping waits for SessionEnd. Without -Mode the script only records.
#
# Safety: a process is recorded only when all three hold:
#   1. its PID is NOT in the session-start snapshot;
#   2. its StartTime is after that snapshot;
#   3. this session's own Claude Code process is in its parent chain
#      (Designer <- DesignerMCP <- claude, TStartup/TServer <- ConsoleMCP <- claude).
# Recording happens while the session is alive, so the parent chain is still intact. At session
# end a recorded process is stopped only if the same PID still has the same name and StartTime,
# so a reused PID is never stopped. Processes started by another Claude session, by a shared HTTP
# MCP bridge, by hand, or detached are left alone and only logged. If this session's process
# cannot be identified, nothing is recorded. The operator's pre-existing Designer / TServer
# processes are NEVER touched.
# /clear and /resume end the session but keep the same Claude Code process and its MCP servers,
# so for those two reasons Reap stops nothing and only logs what it kept.
# For the mid-session case (blocked right now on a .dbsln or bridge port still held by
# an earlier process), use the kill-zombies skill instead.
# (kill-zombies ships in the companion repo: github.com/tatsoft-llc/Claude-Code-Skills)
#
# Test overrides: CLAUDE_REAP_DRYRUN=1 logs what would be stopped and stops nothing;
# CLAUDE_REAP_NAMES=a,b replaces the process-name list.
# ASCII-only on purpose: Windows PowerShell 5.1 reads a BOM-less UTF-8 file as ANSI.

param(
    [ValidateSet('Record', 'Reap')]
    [string]$Mode = 'Record'
)

$ErrorActionPreference = 'SilentlyContinue'
# A hook error must never block the reply or the exit.
trap { exit 0 }

try {
    $raw = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($raw)) { exit 0 }
    $payload = $raw | ConvertFrom-Json
} catch {
    exit 0
}

$sessionId = $payload.session_id
if ([string]::IsNullOrWhiteSpace($sessionId)) { exit 0 }

$stateDir = Join-Path $env:TEMP 'claude-orphan-baselines'
$baselineFile = Join-Path $stateDir "$sessionId.json"
$recordFile = Join-Path $stateDir "$sessionId.spawned.json"
if (-not (Test-Path $baselineFile)) {
    # No snapshot captured - cannot safely distinguish ours from pre-existing. Bail clean.
    exit 0
}

$baseline = Get-Content $baselineFile -Raw | ConvertFrom-Json
$baselinePids = @{}
foreach ($p in $baseline.processes) { $baselinePids[[int]$p.Id] = $true }
# PowerShell 7 already turns the ISO string into a DateTime; 5.1 leaves it a string.
if ($baseline.capturedAt -is [datetime]) { $baselineCutoff = $baseline.capturedAt }
else { try { $baselineCutoff = [datetime]::Parse($baseline.capturedAt) } catch { $baselineCutoff = [datetime]::MinValue } }

function Get-StartTicks($proc) {
    try { return [int64]$proc.StartTime.ToUniversalTime().Ticks } catch { return $null }
}

# Candidates: FrameworX processes started after the snapshot and not in it.
$names = @('Designer', 'TServer', 'TRunModule', 'TStartup')
if ($env:CLAUDE_REAP_NAMES) { $names = $env:CLAUDE_REAP_NAMES -split ',' | ForEach-Object { $_.Trim() } | Where-Object { $_ } }
$candidates = @()
foreach ($proc in (Get-Process $names -ErrorAction SilentlyContinue)) {
    if ($baselinePids.ContainsKey([int]$proc.Id)) { continue }
    $started = $null
    try { $started = $proc.StartTime } catch {}
    if ($started -and $started -gt $baselineCutoff) { $candidates += $proc }
}

# Attribute each candidate by process ancestry. The process table is only built when there is
# a candidate, so a reply that started nothing costs one Get-Process call.
$sessionRoot = $null
$ours = @()
$notOurs = @()
if ($candidates.Count -gt 0) {
    $procTable = @{}
    foreach ($w in (Get-CimInstance Win32_Process -ErrorAction SilentlyContinue)) { $procTable[[int]$w.ProcessId] = $w }

    function Get-AncestorChain([int]$startPid) {
        $chain = @(); $p = $startPid; $guard = 0
        while ($p -and $procTable.ContainsKey($p) -and $guard -lt 64) {
            $chain += $p
            $p = [int]$procTable[$p].ParentProcessId
            $guard++
            if ($chain -contains $p) { break }
        }
        return $chain
    }

    # This hook runs as a descendant of the session's own Claude Code process: the first
    # claude/node ancestor above this script is the session root.
    foreach ($anc in (Get-AncestorChain $PID)) {
        if ($anc -eq $PID) { continue }
        if ($procTable[$anc].Name -match '^(claude|node)(\.exe)?$') { $sessionRoot = $anc; break }
    }

    foreach ($c in $candidates) {
        if ($sessionRoot -and ((Get-AncestorChain ([int]$c.Id)) -contains $sessionRoot)) { $ours += $c } else { $notOurs += $c }
    }
}

# Merge newly attributed processes into this session's record.
$record = @()
if (Test-Path $recordFile) {
    $saved = Get-Content $recordFile -Raw | ConvertFrom-Json
    $record = @($saved.entries | ForEach-Object { $_ })
}
$known = @{}
foreach ($r in $record) { $known["$($r.Id)/$($r.StartTicks)"] = $true }
$added = 0
foreach ($c in $ours) {
    $ticks = Get-StartTicks $c
    if ($null -eq $ticks) { continue }
    $key = "$($c.Id)/$ticks"
    if ($known.ContainsKey($key)) { continue }
    $record += [PSCustomObject]@{
        Id         = [int]$c.Id
        Name       = $c.ProcessName
        StartTicks = $ticks
        StartTime  = $c.StartTime.ToString('o')
    }
    $known[$key] = $true
    $added++
}
# A recorded process whose parent chain has broken since is still ours, not someone else's.
$notOurs = @($notOurs | Where-Object { -not $known.ContainsKey("$($_.Id)/$(Get-StartTicks $_)") })

if ($Mode -eq 'Record') {
    if ($added -gt 0) {
        $tmp = "$recordFile.tmp"
        [PSCustomObject]@{ sessionId = $sessionId; sessionRoot = $sessionRoot; entries = @($record) } |
            ConvertTo-Json -Depth 4 | Out-File -FilePath $tmp -Encoding utf8
        Move-Item -Path $tmp -Destination $recordFile -Force
    }
    exit 0
}

# ---- Reap (SessionEnd) ----
$reason = [string]$payload.reason
$keepRunning = ($reason -eq 'clear' -or $reason -eq 'resume')
$dryRun = ($env:CLAUDE_REAP_DRYRUN -eq '1')

$toStop = @()
$kept = @()
$gone = @()
foreach ($r in $record) {
    $p = Get-Process -Id ([int]$r.Id) -ErrorAction SilentlyContinue
    if (-not $p -or $p.ProcessName -ne $r.Name -or (Get-StartTicks $p) -ne [int64]$r.StartTicks) { $gone += $r; continue }
    if ($keepRunning) { $kept += $p } else { $toStop += $p }
}

if ($toStop.Count -gt 0 -or $kept.Count -gt 0 -or $notOurs.Count -gt 0 -or $dryRun) {
    # Log to the workspace's AISessions directory before stopping anything.
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
        $lines += "## Session $sessionId end @ $now (reason: $(if ($reason) { $reason } else { 'none' }))" + $(if ($dryRun) { ' (DRY RUN)' } else { '' })
        $lines += "Baseline captured: $($baselineCutoff.ToString('o')); recorded: $($record.Count); already gone: $($gone.Count)"
        if ($keepRunning) {
            $lines += "Kept $($kept.Count) process(es) this session started: /$reason keeps the same Claude Code process running."
            foreach ($o in $kept) { $lines += "- $($o.ProcessName) PID=$($o.Id) started=$($o.StartTime.ToString('o'))" }
        } else {
            $lines += "Stopped $($toStop.Count) process(es) this session started:"
            foreach ($o in $toStop) { $lines += "- $($o.ProcessName) PID=$($o.Id) started=$($o.StartTime.ToString('o'))" }
        }
        if ($notOurs.Count -gt 0) {
            $lines += "Left alone $($notOurs.Count) process(es) started after the baseline but NOT spawned by this session (another session, a shared bridge, by hand, or detached):"
            foreach ($o in $notOurs) { $lines += "- $($o.ProcessName) PID=$($o.Id) started=$($o.StartTime.ToString('o'))" }
        }
        $lines += ''
        Add-Content -Path $logFile -Value ($lines -join "`n")
    }
}

if (-not $dryRun) {
    foreach ($o in $toStop) {
        try { Stop-Process -Id $o.Id -Force -ErrorAction SilentlyContinue } catch {}
    }
}

Remove-Item $baselineFile, $recordFile -ErrorAction SilentlyContinue
exit 0
