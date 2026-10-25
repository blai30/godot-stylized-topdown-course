# Probe: the Animation panel's controls, and a first animation made through them.
import sys
sys.path.insert(0, sys.argv[1])
from steps import unfold_inspector, write, eval_, add_node, dump_popups, dump_windows

DUMP = eval_('''
var panel = plugin._find_class(plugin.get_tree().root, "AnimationPlayerEditor")
if panel == null:
	return "no AnimationPlayerEditor"
var out := []
for control in plugin._collect(panel, "", ""):
	if control is BaseButton or control is LineEdit or control is SpinBox or control is OptionButton:
		out.append("%s text '%s' tooltip '%s' name %s" % [control.get_class(), str(control.get("text")), control.tooltip_text, control.name])
print("[probe] anim panel\\n", "\\n".join(out))
''')
steps = [
    {'op': 'sleep', 'seconds': 3},
    {'op': 'open', 'path': 'res://world/environment/world_environment.tscn'},
    {'op': 'wait', 'frames': 40},
    {'op': 'select', 'path': '.'},
    *add_node('AnimationPlayer', 'Day'),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'probe_anim_a', 'frames': 20},
    eval_('''
var panel = plugin._find_class(plugin.get_tree().root, "AnimationPlayerEditor")
for button in plugin._collect(panel, "MenuButton", "Animation"):
	var popup: PopupMenu = button.get_popup()
	var items := []
	for i in popup.item_count:
		items.append(popup.get_item_text(i))
	print("[probe] animation menu ", items)
	for i in popup.item_count:
		if popup.get_item_text(i).begins_with("New"):
			popup.id_pressed.emit(popup.get_item_id(i))
			return ""
'''),
    {'op': 'wait', 'frames': 30},
    dump_windows(),
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is ConfirmationDialog:
		var edit: LineEdit = plugin._collect(window, "LineEdit", "")[0]
		edit.text = "day"
		edit.text_changed.emit("day")
		window.get_ok_button().pressed.emit()
		return ""
return "no new animation dialog"
'''),
    {'op': 'wait', 'frames': 40},
    eval_('''
var panel = plugin._find_class(plugin.get_tree().root, "AnimationPlayerEditor")
for button in plugin._collect(panel, "MenuButton", "Edit"):
	var popup: PopupMenu = button.get_popup()
	var items := []
	for i in popup.item_count:
		items.append(popup.get_item_text(i))
	print("[probe] edit menu ", items)
'''),
    {'op': 'select', 'path': 'Sun'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 30},
    eval_('''
var row = plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "light_energy")
print("[probe] row ", row, " keying ", row.is_keying() if row else "none")
var out := []
for s in row.get_signal_list():
	out.append(s.name)
print("[probe] signals ", out)
row.emit_signal("property_keyed", "light_energy", false)
'''),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'probe_anim_b', 'frames': 20},
    eval_('''
var player := editor.get_edited_scene_root().get_node("Day") as AnimationPlayer
for name in player.get_animation_list():
	var animation := player.get_animation(name)
	print("[probe] animation ", name, " tracks ", animation.get_track_count(), " length ", animation.length)
	for i in animation.get_track_count():
		print("[probe] track ", animation.track_get_path(i), " keys ", animation.track_get_key_count(i))
'''),
]
write(sys.argv[2], steps)
