import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_

write(sys.argv[2], [
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'select', 'path': 'Ground'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 30},
    eval_('''
for button in plugin._collect(plugin.get_tree().root, "MenuButton", ""):
	var rect: Rect2 = button.get_global_rect()
	if rect.position.y < 120:
		var popup: PopupMenu = button.get_popup()
		var items := []
		for i in popup.item_count:
			items.append(popup.get_item_text(i))
		print("[probe] menu button '", button.text, "' tooltip '", button.tooltip_text, "' ", rect, " items ", items)
'''),
    {'op': 'capture', 'name': 'p06_ground_selected', 'frames': 20},
])
