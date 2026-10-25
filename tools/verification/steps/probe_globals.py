# Probe: the Project Settings > Globals > Shader Globals tab.
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, dump_windows, click_tab

FIND = """
var window: Window = null
for candidate in plugin._windows(plugin.get_tree().root):
	if candidate.visible and "Project Settings" in candidate.title:
		window = candidate
if window == null:
	return "no Project Settings window"
"""
steps = [
    {'op': 'sleep', 'seconds': 3},
    {'op': 'menu', 'path': ['Project', 'Project Settings...']},
    {'op': 'wait', 'frames': 60},
    eval_(FIND + """
var out := []
for bar in plugin._collect(window, "TabBar", ""):
	var titles := []
	for i in bar.tab_count:
		titles.append(bar.get_tab_title(i))
	out.append(str(titles))
print("[probe] tab bars ", out)
for bar in plugin._collect(window, "TabBar", ""):
	for i in bar.tab_count:
		if bar.get_tab_title(i) in ["Globals", "Shader Globals"]:
			bar.current_tab = i
			bar.tab_selected.emit(i)
			bar.tab_changed.emit(i)
"""),
    {'op': 'wait', 'frames': 30},
    eval_(FIND + """
for bar in plugin._collect(window, "TabBar", ""):
	for i in bar.tab_count:
		if bar.get_tab_title(i) == "Shader Globals":
			bar.current_tab = i
"""),
    {'op': 'wait', 'frames': 30},
    eval_(FIND + """
var out := []
for bar in plugin._collect(window, "TabBar", ""):
	var titles := []
	for i in bar.tab_count:
		titles.append(bar.get_tab_title(i))
	out.append(str(titles) + " current " + str(bar.current_tab))
print("[probe] tab bars now ", out)
for control in plugin._collect(window, "", ""):
	if control is BaseButton or control is LineEdit or control is OptionButton:
		out.append("%s '%s' tooltip '%s'" % [control.get_class(), str(control.get("text")), control.tooltip_text])
print("[probe] controls\\n", "\\n".join(out))
"""),
    {'op': 'capture', 'name': 'probe_globals', 'window': 'Project Settings'},
]
write(sys.argv[2], steps)
