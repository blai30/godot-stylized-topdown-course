# Opens the workbench in the self-contained editor and replays a steps file; prints the driver's step log and any
# script errors. Probe output stays in the editor log, editor.log.
param([Parameter(Mandatory)][string]$Steps, [string]$Out = "$env:TEMP\sgt-phase1\shots", [int]$TimeoutSeconds = 300)
$env:CAPTURE_STEPS = $Steps
$env:CAPTURE_OUT = $Out
$env:CAPTURE_LOG = "$env:TEMP\sgt-phase1\steps.log"
$godot = "$env:TEMP\sgt-phase1\godot-sc\Godot_v4.8-beta1_mono_win64_console.exe"
$log = "$env:TEMP\sgt-phase1\editor.log"
Remove-Item $log, $env:CAPTURE_LOG -ErrorAction SilentlyContinue
$process = Start-Process $godot -ArgumentList '--editor', '--path', "$env:TEMP\sgt-phase1\workbench", '--resolution', '1920x1080', '--log-file', $log -PassThru -WindowStyle Normal
$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
# The driver logs "[capture] done" after the last step; the editor does not always quit by itself after a game run.
while (-not $process.HasExited -and (Get-Date) -lt $deadline) {
    Start-Sleep -Seconds 2
    if ((Test-Path $env:CAPTURE_LOG) -and (Select-String -Path $env:CAPTURE_LOG -Pattern '^\[capture\] done' -Quiet -ErrorAction SilentlyContinue)) {
        Start-Sleep -Seconds 3
        break
    }
}
if (-not $process.HasExited) {
    if ((Get-Date) -ge $deadline) { Write-Host 'TIMED OUT' }
    Get-Process | Where-Object { $_.Path -like "$env:TEMP\sgt-phase1\godot-sc\*" } | Stop-Process -Force
}
if (Test-Path $env:CAPTURE_LOG) { Get-Content $env:CAPTURE_LOG }
if (Test-Path $log) { Select-String -Path $log -Pattern 'SCRIPT ERROR|^ERROR:' | ForEach-Object { $_.Line } }
