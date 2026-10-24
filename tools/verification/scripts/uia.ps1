# Drives a Godot window through UI Automation (Godot exposes its controls through AccessKit when started with
# --accessibility always), so the system cursor and keyboard are never touched. Used for the Project Manager, which
# the editor plugin cannot reach.
# Usage: uia.ps1 -ProcessId 1234 -List | -Invoke "Create" | -SetValue "Project Name:" -Value "x" | -Toggle "Edit Now"
#   -Select "Forward+" selects a radio button or list item. -Nth picks among elements with the same name, -Type
#   narrows by control type (Edit, Button, ...). -Dialog limits the search to the window with that name.
param([Parameter(Mandatory)][int]$ProcessId, [string]$Dialog, [switch]$List, [string]$Invoke, [string]$SetValue, [string]$Value, [string]$Toggle, [string]$Select, [int]$Nth = 0, [string]$Type)
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes
$automation = [System.Windows.Automation.AutomationElement]
$condition = New-Object System.Windows.Automation.PropertyCondition ($automation::ProcessIdProperty), $ProcessId
$windows = $automation::RootElement.FindAll('Children', $condition)
if ($Dialog) {
	# A native dialog (window class #32770), found by its title; searching the automation tree for it is slow.
	Add-Type -Namespace Uia -Name Native -MemberDefinition '[DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern IntPtr FindWindow(string className, string title);'
	$handle = [Uia.Native]::FindWindow('#32770', $Dialog)
	if ($handle -eq [IntPtr]::Zero) { throw "No dialog named '$Dialog'." }
	$windows = @($automation::FromHandle($handle))
}

function Find-Named([string]$name) {
	$matches = @()
	foreach ($window in $windows) {
		foreach ($element in $window.FindAll('Descendants', [System.Windows.Automation.Condition]::TrueCondition)) {
			$typeOk = (-not $Type) -or $element.Current.ControlType.ProgrammaticName -eq "ControlType.$Type"
			if ($element.Current.Name -eq $name -and $typeOk) { $matches += $element }
		}
	}
	if ($matches.Count -le $Nth) { throw "No element named '$name' (index $Nth)." }
	return $matches[$Nth]
}

if ($List) {
	foreach ($window in $windows) {
		"== " + $window.Current.Name
		foreach ($element in $window.FindAll('Descendants', [System.Windows.Automation.Condition]::TrueCondition)) {
			$text = ''
			$pattern = $null
			if ($element.TryGetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern, [ref]$pattern)) { $text = ' = ' + $pattern.Current.Value }
			if ($element.TryGetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern, [ref]$pattern)) { $text = ' [' + $pattern.Current.ToggleState + ']' }
			if ($element.TryGetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern, [ref]$pattern)) { $text += ' (selected: ' + $pattern.Current.IsSelected + ')' }
			"{0} | {1}{2}" -f $element.Current.ControlType.ProgrammaticName.Replace('ControlType.', ''), $element.Current.Name, $text
		}
	}
}
if ($Invoke) {
	(Find-Named $Invoke).GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
	"invoked $Invoke"
}
if ($SetValue) {
	(Find-Named $SetValue).GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).SetValue($Value)
	"set $SetValue"
}
if ($Toggle) {
	(Find-Named $Toggle).GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern).Toggle()
	"toggled $Toggle"
}
if ($Select) {
	(Find-Named $Select).GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern).Select()
	"selected $Select"
}
