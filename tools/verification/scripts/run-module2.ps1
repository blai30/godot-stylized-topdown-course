# Replays Module 2 in order: lesson 7 in Krita, 8 to 10 in Blender, 11 in Godot, 12 in Blender then Godot. Each lesson
# starts from the snapshot the one before saved; the chain stops at the first failure. Lesson 8 changes only Blender's
# user folder, which it saves for lesson 9.
# Usage: run-module2.ps1 [-From 7]
param([int]$From = 7)
$scripts = $PSScriptRoot
$snapshots = "$env:TEMP\sgt-phase1\snapshots"
$workbench = "$env:TEMP\sgt-phase1\workbench"
$blend = "$workbench\art_source\nature"

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

function Save-User([string]$Name) {
    $users = "$env:TEMP\sgt-phase2\blender-users"
    Remove-Item -Recurse -Force "$users\$Name" -ErrorAction SilentlyContinue
    Copy-Item -Recurse "$env:TEMP\sgt-phase2\blender-user" "$users\$Name"
}

if ($From -le 7) {
    & "$scripts\reset-workbench.ps1" -Snapshot lesson-06 | Out-Null
    Check (& "$scripts\run-krita.ps1" -Script lesson07 -TimeoutSeconds 600) 'lesson 7'
    Save-Snapshot lesson-07
}
if ($From -le 8) {
    & "$scripts\reset-workbench.ps1" -Snapshot lesson-07 | Out-Null
    Check (& "$scripts\run-blender.ps1" -Script lesson08 -SaveUser lesson-08 -TimeoutSeconds 300) 'lesson 8'
    Save-Snapshot lesson-08
}
if ($From -le 9) {
    & "$scripts\reset-workbench.ps1" -Snapshot lesson-08 | Out-Null
    Check (& "$scripts\run-blender.ps1" -Script lesson09 -User lesson-08 -TimeoutSeconds 300) 'lesson 9'
    Save-User lesson-09
    Save-Snapshot lesson-09
}
if ($From -le 10) {
    & "$scripts\reset-workbench.ps1" -Snapshot lesson-09 | Out-Null
    Check (& "$scripts\run-blender.ps1" -Script lesson10 -User lesson-09 -Open "$blend\rock_small\rock_small.blend" -TimeoutSeconds 300) 'lesson 10'
    Save-User lesson-10
    Save-Snapshot lesson-10
}
if ($From -le 11) {
    Check (& "$scripts\run-lesson.ps1" -Script lesson11 -Snapshot lesson-10 -TimeoutSeconds 400) 'lesson 11'
    Get-Content "$env:TEMP\sgt-phase1\game-l11.log" | Where-Object { $_ -match 'player' }
    Copy-Item "$env:TEMP\sgt-phase1\editor.log" "$env:TEMP\sgt-phase1\editor-lesson11.log" -Force
    Save-Snapshot lesson-11
}
if ($From -le 12) {
    & "$scripts\reset-workbench.ps1" -Snapshot lesson-11 | Out-Null
    Check (& "$scripts\run-blender.ps1" -Script lesson12 -User lesson-10 -Open "$blend\rock_small\rock_small.blend" -TimeoutSeconds 300) 'lesson 12 in Blender'
    Save-User lesson-12
    Save-Snapshot lesson-12a
    Check (& "$scripts\run-lesson.ps1" -Script lesson12 -Snapshot lesson-12a -TimeoutSeconds 400) 'lesson 12 in Godot'
    Get-Content "$env:TEMP\sgt-phase1\game-l12.log" | Where-Object { $_ -match 'player' }
    Copy-Item "$env:TEMP\sgt-phase1\editor.log" "$env:TEMP\sgt-phase1\editor-lesson12.log" -Force
    Save-Snapshot lesson-12
}
"chain done"
