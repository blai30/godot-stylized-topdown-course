# Runs a Krita step script (tools/verification/krita-steps/<Script>.py) through the driver plugin.
# Krita keeps its settings in fixed places, so the owner's Krita files are moved aside first and put back afterward,
# and everything the run created is removed.
# Usage: run-krita.ps1 -Script probe07 [-Out <shots folder>]
param([Parameter(Mandatory)][string]$Script, [string]$Out = "$env:TEMP\sgt-phase2\shots\krita", [int]$TimeoutSeconds = 300)
$verification = Split-Path $PSScriptRoot
$work = "$env:TEMP\sgt-phase2"
$backup = "$work\krita-backup"
$items = "$env:LOCALAPPDATA\kritarc", "$env:LOCALAPPDATA\kritadisplayrc", "$env:LOCALAPPDATA\krita", "$env:LOCALAPPDATA\krita.log", "$env:LOCALAPPDATA\krita-sysinfo.log", "$env:APPDATA\krita"
# A leftover backup means an earlier run never restored; restore it by hand before running again.
if (Test-Path $backup) { throw "Backup folder $backup exists; restore it before running." }
New-Item -ItemType Directory -Force $backup, $Out | Out-Null
$moved = @()
foreach ($item in $items) {
    if (Test-Path $item) {
        $name = ($item -replace '[:\\]', '_')
        Move-Item $item "$backup\$name"
        $moved += [pscustomobject]@{ Item = $item; Saved = "$backup\$name" }
    }
}
try {
    $plugins = "$env:APPDATA\krita\pykrita"
    New-Item -ItemType Directory -Force $plugins | Out-Null
    Copy-Item "$verification\krita-driver\*" $plugins -Recurse -Force
    [System.IO.File]::WriteAllText("$env:LOCALAPPDATA\kritarc", "[python]`nenable_sgt_driver=true`n")
    $env:KRITA_STEPS = "$verification\krita-steps\$Script.py"
    $env:KRITA_OUT = $Out
    $env:KRITA_LOG = "$work\krita-steps.log"
    Remove-Item $env:KRITA_LOG -ErrorAction SilentlyContinue
    # The console build writes Python errors to its output.
    $process = Start-Process 'C:\Program Files\Krita (x64)\bin\krita.com' -ArgumentList '--nosplash' -PassThru -RedirectStandardOutput "$work\krita-out.txt" -RedirectStandardError "$work\krita-err.txt"
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while (-not $process.HasExited -and (Get-Date) -lt $deadline) {
        Start-Sleep -Seconds 2
        if ((Test-Path $env:KRITA_LOG) -and (Select-String -Path $env:KRITA_LOG -Pattern '^\[krita\] done' -Quiet)) { break }
    }
    if ((Get-Date) -ge $deadline) { Write-Host 'TIMED OUT' }
    if (-not $process.HasExited) { Stop-Process -Id $process.Id -Force; Start-Sleep -Seconds 2 }
    if (Test-Path $env:KRITA_LOG) { Get-Content $env:KRITA_LOG }
}
finally {
    # Krita's own log explains plugin load failures.
    Copy-Item "$env:LOCALAPPDATA\krita.log" "$work\krita.log" -ErrorAction SilentlyContinue
    foreach ($item in $items) { if (Test-Path $item) { Remove-Item -Recurse -Force $item } }
    foreach ($entry in $moved) { Move-Item $entry.Saved $entry.Item }
    Remove-Item -Recurse -Force $backup
}
