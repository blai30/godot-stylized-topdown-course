# Probe: collapsing the bottom panel by clicking its current tab.
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, click_tab

REPORT = eval_('''
for bar in plugin._collect(plugin.get_tree().root, "TabBar", ""):
	var titles := []
	for i in bar.tab_count:
		titles.append(bar.get_tab_title(i))
	if "Output" in titles:
		print("[probe] bottom bar current ", bar.current_tab, " titles ", titles)
		var panel = bar.get_parent()
		print("[probe] parent ", panel.get_class(), " ", panel.get_parent().get_class(), " size ", panel.get_parent().size)
''')
steps = [
    {'op': 'sleep', 'seconds': 3},
    REPORT,
    click_tab('Output'),
    {'op': 'wait', 'frames': 20},
    REPORT,
    {'op': 'capture', 'name': 'probe_a', 'frames': 10},
    click_tab('Output'),
    {'op': 'wait', 'frames': 20},
    REPORT,
    {'op': 'capture', 'name': 'probe_b', 'frames': 10},
]
write(sys.argv[2], steps)
