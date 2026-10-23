# Sends synthetic mouse clicks and typed text to one window through its message queue (PostMessage), so the system
# cursor and keyboard are never touched. Used for the Project Manager, which the editor plugin cannot reach.
# Usage: post-input.ps1 -ProcessId 1234 -Click 640,360 [-Double] | -Text "abc" | -Key 0x0D
param([Parameter(Mandatory)][int]$ProcessId, [int[]]$Click, [switch]$Double, [string]$Text, [int]$Key)
Add-Type @'
using System;
using System.Runtime.InteropServices;
using System.Text;
public static class PostInput {
    public delegate bool EnumProc(IntPtr hwnd, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc proc, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hwnd);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint pid);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetWindowText(IntPtr hwnd, StringBuilder text, int max);
    [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr hwnd, uint message, IntPtr wParam, IntPtr lParam);
}
'@
$script:found = [IntPtr]::Zero
$callback = [PostInput+EnumProc]{
    param($hwnd, $lParam)
    $windowPid = 0
    [void][PostInput]::GetWindowThreadProcessId($hwnd, [ref]$windowPid)
    $title = New-Object System.Text.StringBuilder 512
    [void][PostInput]::GetWindowText($hwnd, $title, 512)
    if ($windowPid -eq $ProcessId -and [PostInput]::IsWindowVisible($hwnd) -and $title.Length -gt 0) { $script:found = $hwnd; return $false }
    return $true
}
[void][PostInput]::EnumWindows($callback, [IntPtr]::Zero)
if ($script:found -eq [IntPtr]::Zero) { throw "No visible window for process $ProcessId." }
$hwnd = $script:found
if ($Click) {
    $point = [IntPtr](($Click[1] -shl 16) -bor ($Click[0] -band 0xFFFF))
    # WM_MOUSEMOVE, then WM_LBUTTONDOWN (MK_LBUTTON) and WM_LBUTTONUP; a double click adds WM_LBUTTONDBLCLK.
    [void][PostInput]::PostMessage($hwnd, 0x0200, [IntPtr]0, $point)
    Start-Sleep -Milliseconds 100
    [void][PostInput]::PostMessage($hwnd, 0x0201, [IntPtr]1, $point)
    Start-Sleep -Milliseconds 50
    [void][PostInput]::PostMessage($hwnd, 0x0202, [IntPtr]0, $point)
    if ($Double) {
        Start-Sleep -Milliseconds 50
        [void][PostInput]::PostMessage($hwnd, 0x0203, [IntPtr]1, $point)
        Start-Sleep -Milliseconds 50
        [void][PostInput]::PostMessage($hwnd, 0x0202, [IntPtr]0, $point)
    }
}
if ($Text) {
    # WM_CHAR per character.
    foreach ($char in $Text.ToCharArray()) {
        [void][PostInput]::PostMessage($hwnd, 0x0102, [IntPtr][int]$char, [IntPtr]1)
        Start-Sleep -Milliseconds 20
    }
}
if ($Key) {
    # WM_KEYDOWN and WM_KEYUP for a virtual key code.
    [void][PostInput]::PostMessage($hwnd, 0x0100, [IntPtr]$Key, [IntPtr]1)
    Start-Sleep -Milliseconds 50
    [void][PostInput]::PostMessage($hwnd, 0x0101, [IntPtr]$Key, [IntPtr]0xC0000001)
}
"posted to $hwnd"
