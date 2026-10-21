# PreToolUse hook: pauses new-solution creation when CPU > 90%, so a Designer/Console
# process starts only once the machine has headroom to service it. Audience-neutral resource guard;
# does NOT inspect the solution name (no sandbox-prefix enforcement: that's prose, not a hook).
# Matcher (settings.json): ^mcp__.+__(create_solution|create_solution_file|create_workspace)$
# Input : JSON on stdin (ignored).
# Output: when blocked, a PreToolUse permissionDecision=deny JSON on stdout, which refuses the
#   call. (continue:false would let the call run and only end the turn after it.) Exit 0 always.
# Errors: a script error prints a warning (systemMessage) and lets the call through.
# ASCII-only on purpose: Windows PowerShell 5.1 reads a BOM-less UTF-8 file as ANSI,
# and a non-ASCII byte inside a string can end the string early and break the parse.

function Write-Deny([string]$reason) {
    [ordered]@{
        hookSpecificOutput = [ordered]@{
            hookEventName            = 'PreToolUse'
            permissionDecision       = 'deny'
            permissionDecisionReason = $reason
        }
    } | ConvertTo-Json -Compress -Depth 4
}

trap {
    [ordered]@{ systemMessage = "CPU check hook error ($($_.Exception.Message)); solution creation allowed without the check." } | ConvertTo-Json -Compress
    exit 0
}

$null = [Console]::In.ReadToEnd()
$started = Get-Date

# Each CPU read is bounded, so the hook answers inside its timeout. On a loaded machine
# one read can take about 10 s; a slow first read is already the answer, so the second
# read (to ride out a short spike) runs only when the first one was quick.
$cpu = [int]((Get-CimInstance Win32_Processor -OperationTimeoutSec 12 -ErrorAction Stop | Measure-Object -Property LoadPercentage -Average).Average)

if ($cpu -gt 90 -and ((Get-Date) - $started).TotalSeconds -lt 7) {
    Start-Sleep -Seconds 5
    $cpu = [int]((Get-CimInstance Win32_Processor -OperationTimeoutSec 8 -ErrorAction Stop | Measure-Object -Property LoadPercentage -Average).Average)
}

if ($cpu -gt 90) {
    Write-Deny "CPU at ${cpu}% (threshold: 90%). Solution creation paused: wait for CPU to drop below 90% and retry."
    exit 0
}

exit 0
