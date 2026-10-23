# Restores the workbench to a snapshot, keeping Godot's import cache.
param([Parameter(Mandatory)][string]$Snapshot)
$w = "$env:TEMP\sgt-phase1\workbench"
Get-ChildItem -Force $w | Where-Object { $_.Name -notin '.godot', '.capture' } | Remove-Item -Recurse -Force
Get-ChildItem -Force "$env:TEMP\sgt-phase1\snapshots\$Snapshot" | Where-Object { $_.Name -notin '.godot', '.capture' } | Copy-Item -Destination $w -Recurse -Force
"reset to $Snapshot"
# The editor remembers each scene's camera and docks under .godot/editor; a reader opening the scene starts fresh.
Remove-Item -Recurse -Force "$w\.godot\editor" -ErrorAction SilentlyContinue
