# PreToolUse hook: pauses new-solution creation when CPU > 90%, so a Designer/Console
# process starts only once the machine has headroom to service it. Audience-neutral resource guard;
# does NOT inspect the solution name (no sandbox-prefix enforcement: that's prose, not a hook).
# Input : JSON on stdin (ignored). Output: JSON {continue:false, stopReason} when blocked.

$null = [Console]::In.ReadToEnd()

$cpu = [int]((Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average)

if ($cpu -gt 90) {
    Start-Sleep -Seconds 5
    $cpu = [int]((Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average)
}

if ($cpu -gt 90) {
    [ordered]@{
        continue   = $false
        stopReason = "CPU at ${cpu}% (threshold: 90%). Solution creation paused, wait for CPU to drop below 90% and retry."
    } | ConvertTo-Json -Compress
    exit 1
}

exit 0
