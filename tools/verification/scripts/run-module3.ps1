# Replays Module 3 in order: lessons 13 and 14 in Krita then Godot, 15 to 18 in Godot. Each lesson starts from the
# snapshot the one before saved; the chain stops at the first failure.
# Usage: run-module3.ps1 [-From 13]
param([int]$From = 13)
$scripts = $PSScriptRoot
$snapshots = "$env:TEMP\sgt-phase1\snapshots"
$workbench = "$env:TEMP\sgt-phase1\workbench"

function Save-Snapshot([string]$Name) {
    Remove-Item -Recurse -Force "$snapshots\$Name" -ErrorAction SilentlyContinue
    New-Item -ItemType Directory "$snapshots\$Name" | Out-Null
    Get-ChildItem -Force $workbench | Where-Object { $_.Name -notin '.godot', '.capture' } | Copy-Item -Destination "$snapshots\$Name" -Recurse -Force
    "saved $Name"
}

function Check([string[]]$Lines, [string]$Lesson) {
    $Lines | Where-Object { $_ -match 'FAILED|TIMED OUT|SCRIPT ERROR|stopped' }
    if ($Lines -match 'FAILED|TIMED OUT|SCRIPT ERROR|stopped') { "chain stopped at $Lesson"; exit 1 }
}

if ($From -le 13) {
    & "$scripts\reset-workbench.ps1" -Snapshot lesson-12 | Out-Null
    $lines = & "$scripts\run-krita.ps1" -Script lesson13 -SaveUser lesson-13 -TimeoutSeconds 1500
    $lines | Set-Content "$env:TEMP\sgt-phase2\krita-lesson13.log"
    Check $lines 'lesson 13 in Krita'
    Check (& "$scripts\run-lesson.ps1" -Script lesson13 -TimeoutSeconds 300) 'lesson 13 in Godot'
    Get-Content "$env:TEMP\sgt-phase1\editor.log" | Where-Object { $_ -match '\[probe\] grass' }
    Save-Snapshot lesson-13
}
if ($From -le 14) {
    # Lesson 14 reuses lesson 13's brushes, so Krita starts from its settings as lesson 13 left them.
    & "$scripts\reset-workbench.ps1" -Snapshot lesson-13 | Out-Null
    $lines = & "$scripts\run-krita.ps1" -Script lesson14 -User lesson-13 -SaveUser lesson-14 -TimeoutSeconds 2400
    $lines | Set-Content "$env:TEMP\sgt-phase2\krita-lesson14.log"
    Check $lines 'lesson 14 in Krita'
    Check (& "$scripts\run-lesson.ps1" -Script lesson14 -TimeoutSeconds 300) 'lesson 14 in Godot'
    Get-Content "$env:TEMP\sgt-phase1\editor.log" | Where-Object { $_ -match '\[probe\] (dirt|sand)' }
    Save-Snapshot lesson-14
}
if ($From -le 15) {
    Check (& "$scripts\run-lesson.ps1" -Script lesson15 -Snapshot lesson-14 -TimeoutSeconds 400) 'lesson 15'
    Get-Content "$env:TEMP\sgt-phase1\editor.log" | Where-Object { $_ -match '\[probe\] (tile|texture|newer on disk)' }
    Save-Snapshot lesson-15
}
if ($From -le 16) {
    Check (& "$scripts\run-lesson.ps1" -Script lesson16 -Snapshot lesson-15 -TimeoutSeconds 500) 'lesson 16'
    Get-Content "$env:TEMP\sgt-phase1\game-l16.log" | Where-Object { $_ -match 'player' }
    Save-Snapshot lesson-16
}
if ($From -le 17) {
    Check (& "$scripts\run-lesson.ps1" -Script lesson17 -Snapshot lesson-16 -TimeoutSeconds 600) 'lesson 17'
    Get-Content "$env:TEMP\sgt-phase1\game-l17.log" | Where-Object { $_ -match 'player' }
    Save-Snapshot lesson-17
}
"chain done"
