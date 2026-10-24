# Runs a Blender step script (tools/verification/blender-steps/<Script>.py) through the driver, with Blender's user
# folder (preferences and startup file) in the working area instead of the owner's. The run starts from a saved user
# folder, or from none (a first launch), and can save the folder it leaves for the next lesson.
# Usage: run-blender.ps1 -Script lesson08 [-User fresh|<saved name>] [-SaveUser <name>] [-Open <file.blend>]
param([Parameter(Mandatory)][string]$Script, [string]$User = 'fresh', [string]$SaveUser, [string]$Open, [int]$TimeoutSeconds = 600)
$verification = Split-Path $PSScriptRoot
$work = "$env:TEMP\sgt-phase2"
$users = "$work\blender-users"
$env:BLENDER_USER_RESOURCES = "$work\blender-user"
# Each folder is set as well: with only BLENDER_USER_RESOURCES, Blender 5.2 still read the owner's recent files.
$env:BLENDER_USER_CONFIG = "$work\blender-user\config"
$env:BLENDER_USER_SCRIPTS = "$work\blender-user\scripts"
$env:BLENDER_USER_DATAFILES = "$work\blender-user\datafiles"
$env:BLENDER_USER_EXTENSIONS = "$work\blender-user\extensions"
$env:BLENDER_STEPS = "$verification\blender-steps\$Script.py"
$env:BLENDER_OUT = "$work\shots\blender"
$env:BLENDER_LOG = "$work\blender-steps.log"
New-Item -ItemType Directory -Force $env:BLENDER_OUT, $users | Out-Null
Remove-Item -Recurse -Force $env:BLENDER_USER_RESOURCES, $env:BLENDER_LOG -ErrorAction SilentlyContinue
if ($User -ne 'fresh') { Copy-Item -Recurse "$users\$User" $env:BLENDER_USER_RESOURCES }
# The folders must exist: for a missing one, Blender falls back to the owner's own Blender folder and reads its
# preferences and recent files.
New-Item -ItemType Directory -Force $env:BLENDER_USER_CONFIG, $env:BLENDER_USER_SCRIPTS, $env:BLENDER_USER_DATAFILES, $env:BLENDER_USER_EXTENSIONS | Out-Null
$arguments = @('--window-geometry', '0', '0', '1920', '1080', '--enable-event-simulate')
if ($Open) { $arguments = @("`"$Open`"") + $arguments }
$arguments += @('--python', "`"$verification\blender-steps\driver.py`"")
$process = Start-Process 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -ArgumentList $arguments -PassThru -RedirectStandardOutput "$work\blender-out.txt" -RedirectStandardError "$work\blender-err.txt"
if (-not $process.WaitForExit($TimeoutSeconds * 1000)) { Write-Host 'TIMED OUT'; Stop-Process -Id $process.Id -Force }
if (Test-Path $env:BLENDER_LOG) { Get-Content $env:BLENDER_LOG }
$failed = (-not (Test-Path $env:BLENDER_LOG)) -or (Select-String -Path $env:BLENDER_LOG -Pattern '^FAILED' -Quiet)
if ($SaveUser -and -not $failed) {
    Remove-Item -Recurse -Force "$users\$SaveUser" -ErrorAction SilentlyContinue
    Copy-Item -Recurse $env:BLENDER_USER_RESOURCES "$users\$SaveUser"
    "saved user folder $SaveUser"
}
