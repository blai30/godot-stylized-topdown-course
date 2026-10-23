# Writes a driver steps file: each argument after the output path is one step as a Python dict literal, or the
# helper functions below are imported by step scripts.
import json
import sys


def write(path, steps):
    with open(path, 'w', encoding='utf-8', newline='\n') as file:
        for step in steps:
            file.write(json.dumps(step) + '\n')


def eval_(code):
    return {'op': 'eval', 'code': code.strip('\n')}


def dump_popups():
    return eval_('''
var out := []
for window in plugin._windows(plugin.get_tree().root):
	if window is PopupMenu and window.visible:
		for i in window.item_count:
			out.append(window.get_item_text(i))
print("[probe] popup ", out)
''')


def dump_windows():
    return eval_('''
var out := []
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window != plugin.get_window():
		out.append(window.title + " <" + window.get_class() + ">")
		for control in plugin._collect(window, "", ""):
			if control is Label or control is BaseButton or control is LineEdit:
				out.append("  " + control.get_class() + ": " + str(control.get("text")))
print("[probe] windows\n", "\n".join(out))
''')
