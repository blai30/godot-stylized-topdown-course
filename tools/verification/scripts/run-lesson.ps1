# Resets the workbench to a snapshot, compiles a step script, and replays it in the editor.
# Usage: run-lesson.ps1 -Script lesson03 -Snapshot lesson-02 [-Out <shots folder>]
param([Parameter(Mandatory)][string]$Script, [string]$Snapshot, [string]$Out = "$env:TEMP\sgt-phase2\shots", [int]$TimeoutSeconds = 300)
$verification = Split-Path $PSScriptRoot
$steps = "$env:TEMP\sgt-phase1\steps-$Script.jsonl"
if ($Snapshot) { & "$PSScriptRoot\reset-workbench.ps1" -Snapshot $Snapshot }
Copy-Item "$verification\godot-driver\*" "$env:TEMP\sgt-phase1\workbench\.capture" -Force
# The drivers are registered in the workbench only, never in a snapshot, so every run has both whatever it started from.
$project = "$env:TEMP\sgt-phase1\workbench\project.godot"
$text = Get-Content $project -Raw
if ($text -notmatch 'res://\.capture/plugin\.cfg') { $text += "`n[editor_plugins]`n`nenabled=PackedStringArray(`"res://.capture/plugin.cfg`")`n" }
if ($text -notmatch 'GameDriver=') { $text += "`n[autoload]`n`nGameDriver=`"*res://.capture/game_driver.gd`"`n" }
[System.IO.File]::WriteAllText($project, $text.Replace("`r`n", "`n"))
python "$verification\steps\$Script.py" "$verification\steps" $steps
if ($LASTEXITCODE -ne 0) { throw "Step script $Script failed." }
& "$PSScriptRoot\run-steps.ps1" -Steps $steps -Out $Out -TimeoutSeconds $TimeoutSeconds | Where-Object { $_ -match 'FAILED|stopped|TIMED OUT|\[probe\]|SCRIPT ERROR' }
