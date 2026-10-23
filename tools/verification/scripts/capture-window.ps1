# Saves a PNG of a top-level window, found by process id or by a title substring, using PrintWindow so the window
# need not be in front. Usage: capture-window.ps1 -Title "Godot" -Out C:\path\shot.png [-ProcessId 1234]
param([string]$Title, [int]$ProcessId, [Parameter(Mandatory)][string]$Out)
Add-Type -AssemblyName System.Drawing
Add-Type @'
using System;
using System.Runtime.InteropServices;
using System.Text;
public static class WindowCapture {
    public delegate bool EnumProc(IntPtr hwnd, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc proc, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hwnd);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetWindowText(IntPtr hwnd, StringBuilder text, int max);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint pid);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hwnd, out RECT rect);
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hwnd, IntPtr hdc, uint flags);
    [DllImport("dwmapi.dll")] public static extern int DwmGetWindowAttribute(IntPtr hwnd, int attribute, out RECT rect, int size);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
}
'@
$found = [IntPtr]::Zero
$callback = [WindowCapture+EnumProc]{
    param($hwnd, $lParam)
    if (-not [WindowCapture]::IsWindowVisible($hwnd)) { return $true }
    $text = New-Object System.Text.StringBuilder 512
    [void][WindowCapture]::GetWindowText($hwnd, $text, 512)
    $windowPid = 0
    [void][WindowCapture]::GetWindowThreadProcessId($hwnd, [ref]$windowPid)
    $titleOk = (-not $Title) -or $text.ToString().Contains($Title)
    $pidOk = ($ProcessId -eq 0) -or ($windowPid -eq $ProcessId)
    if ($titleOk -and $pidOk -and $text.Length -gt 0) { $script:found = $hwnd; return $false }
    return $true
}
[void][WindowCapture]::EnumWindows($callback, [IntPtr]::Zero)
if ($found -eq [IntPtr]::Zero) { throw "No visible window matched title '$Title' pid $ProcessId." }
$rect = New-Object WindowCapture+RECT
[void][WindowCapture]::GetWindowRect($found, [ref]$rect)
$width = $rect.Right - $rect.Left; $height = $rect.Bottom - $rect.Top
$bitmap = New-Object System.Drawing.Bitmap $width, $height
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$hdc = $graphics.GetHdc()
# 2 = PW_RENDERFULLCONTENT, which captures GPU-rendered windows.
[void][WindowCapture]::PrintWindow($found, $hdc, 2)
$graphics.ReleaseHdc($hdc)
# Trim the invisible resize border that GetWindowRect includes.
$frame = New-Object WindowCapture+RECT
[void][WindowCapture]::DwmGetWindowAttribute($found, 9, [ref]$frame, 16)
$crop = New-Object System.Drawing.Rectangle ($frame.Left - $rect.Left), ($frame.Top - $rect.Top), ($frame.Right - $frame.Left), ($frame.Bottom - $frame.Top)
$bitmap.Clone($crop, $bitmap.PixelFormat).Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
Write-Host "Saved $Out ($($crop.Width)x$($crop.Height))"
