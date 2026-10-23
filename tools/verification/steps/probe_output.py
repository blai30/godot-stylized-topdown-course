import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_

write(sys.argv[2], [
    eval_('''
var log = plugin._find_class(plugin.get_tree().root, "EditorLog")
print("[probe] editor log ", log)
for button in log.find_children("*", "BaseButton", true, false):
	print("[probe] log button ", button.get_class(), " '", button.tooltip_text.replace("\\n", " | "), "' shortcut '", button.shortcut.get_as_text() if button.shortcut else "", "'")
'''),
])
