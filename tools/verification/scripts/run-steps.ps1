# Opens the workbench in the self-contained editor and replays a steps file; prints the driver's log lines.
param([Parameter(Mandatory)][string]$Steps, [string]$Out = "$env:TEMP\sgt-phase1\shots", [int]$TimeoutSeconds = 300)
$env:CAPTURE_STEPS = $Steps
$env:CAPTURE_OUT = $Out
$godot = "$env:TEMP\sgt-phase1\godot-sc\Godot_v4.8-beta1_mono_win64_console.exe"
$log = "$env:TEMP\sgt-phase1\editor.log"
$process = Start-Process $godot -ArgumentList '--editor', '--path', "$env:TEMP\sgt-phase1\workbench", '--resolution', '1920x1080', '--log-file', $log -PassThru -WindowStyle Normal
if (-not $process.WaitForExit($TimeoutSeconds * 1000)) { $process.Kill(); Write-Host 'TIMED OUT' }
Select-String -Path $log -Pattern '\[capture\]|SCRIPT ERROR|ERROR:' | ForEach-Object { $_.Line }
