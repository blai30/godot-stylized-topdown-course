# Replays lessons in order, each from the snapshot the previous one saved, and stops at the first failure.
# Usage: run-chain.ps1 -From 3 -To 6
param([int]$From = 2, [int]$To = 6)
$snapshots = "$env:TEMP\sgt-phase1\snapshots"
for ($lesson = $From; $lesson -le $To; $lesson++) {
    $script = 'lesson{0:d2}' -f $lesson
    $previous = 'lesson-{0:d2}' -f ($lesson - 1)
    $target = 'lesson-{0:d2}' -f $lesson
    "== $script from $previous"
    $lines = & "$PSScriptRoot\run-lesson.ps1" -Script $script -Snapshot $previous -TimeoutSeconds 590
    $lines | Where-Object { $_ -notmatch ' ok$' }
    # Keep each lesson's logs; the next run overwrites the shared ones.
    Copy-Item "$env:TEMP\sgt-phase1\steps.log" "$env:TEMP\sgt-phase1\steps-$script.log" -Force -ErrorAction SilentlyContinue
    Copy-Item "$env:TEMP\sgt-phase1\editor.log" "$env:TEMP\sgt-phase1\editor-$script.log" -Force -ErrorAction SilentlyContinue
    if ($lines -match 'FAILED|stopped|TIMED OUT|SCRIPT ERROR') { "chain stopped: $target not saved"; exit 1 }
    Remove-Item -Recurse -Force "$snapshots\$target" -ErrorAction SilentlyContinue
    New-Item -ItemType Directory "$snapshots\$target" | Out-Null
    Get-ChildItem -Force "$env:TEMP\sgt-phase1\workbench" | Where-Object { $_.Name -notin '.godot', '.capture' } | Copy-Item -Destination "$snapshots\$target" -Recurse -Force
    "saved $target"
    Get-ChildItem "$env:TEMP\sgt-phase1\game-l$('{0:d2}' -f $lesson)*.log" -ErrorAction SilentlyContinue | ForEach-Object { Get-Content $_ | Where-Object { $_ -notmatch ' ok$' } }
    Select-String -Path "$env:TEMP\sgt-phase1\editor.log" -Pattern '^\[probe\] (file dialog|delete|section after|rows after|new collision)' | ForEach-Object Line
}
