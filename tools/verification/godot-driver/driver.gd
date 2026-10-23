@tool
extends EditorPlugin

# Replays the steps in the JSON file named by the CAPTURE_STEPS environment variable, one per line:
#   {"op": "wait", "frames": 60}
#   {"op": "menu", "path": ["Project", "Tools", "C#", "Create C# solution"]}
#   {"op": "open", "path": "res://x.tscn"}            opens a scene, or any resource in its editor
#   {"op": "select", "path": "Root/Child"}             selects a node in the edited scene
#   {"op": "fs", "path": "res://art/ground"}           shows a path in the FileSystem dock
#   {"op": "main_screen", "name": "3D"}
#   {"op": "capture", "name": "file", "window": ""}    main window, or the visible window whose title contains this
#   {"op": "eval", "code": "..."}                      runs GDScript with `plugin` and `editor` bound, for setup only
#   {"op": "click", "find": {...}, "item": "ground", "button": "right", "double": false}
#       find: {"class": "FileSystemDock"} or {"window": "Create Shader"} plus optional "text" (a Button/Label text) or
#       "nth" (index among matches of "type"); "item" picks a Tree item by text inside the found control
#   {"op": "key", "find": {...}, "key": "F", "ctrl": false, "shift": false}
#   {"op": "popup", "text": "Shader..."}               presses a visible popup menu's item by text, searching submenus
#   {"op": "set_text", "find": {"window": "Create Shader", "type": "LineEdit", "nth": 0}, "text": "..."}
#   {"op": "press", "find": {"window": "Create Shader", "type": "Button", "text": "Create"}}
#   {"op": "quit"}
# Every step logs "[capture] <op> ok" or "[capture] <op> FAILED: <reason>" to the CAPTURE_LOG file.

var _out_dir := ""

func _enter_tree() -> void:
	_run.call_deferred()

func _run() -> void:
	var steps_path := OS.get_environment("CAPTURE_STEPS")
	if steps_path == "":
		return
	_out_dir = OS.get_environment("CAPTURE_OUT")
	DirAccess.make_dir_recursive_absolute(_out_dir)
	# Screenshots are 1920x1080 at 100% editor scale, whatever the display.
	var window := get_window()
	window.mode = Window.MODE_WINDOWED
	window.size = Vector2i(1920, 1080)
	window.position = Vector2i(40, 40)
	await _settle()
	for line in FileAccess.get_file_as_string(steps_path).split("\n", false):
		var step: Dictionary = JSON.parse_string(line)
		var error: String = await _do(step)
		_log("[capture] %s %s%s" % [step.get("op"), step.get("name", step.get("path", "")), " ok" if error == "" else " FAILED: " + error])
		# A failed step leaves the editor in an unknown state, so nothing after it is trustworthy.
		if error != "" and not step.get("optional", false):
			_log("[capture] stopped")
			break
	# After a game session the editor may not quit on its own, so run-steps.ps1 closes it when it sees this line.
	_log("[capture] done")
	get_tree().quit()

# Step results go to the file named by CAPTURE_LOG, not the Output panel, so they never show in captures of it. The file
# stays open for the whole run: reopening it per line fails while run-steps.ps1 is reading it, and loses lines.
var _log_file: FileAccess = null

func _log(text: String) -> void:
	if _log_file == null:
		_log_file = FileAccess.open(OS.get_environment("CAPTURE_LOG"), FileAccess.WRITE)
	_log_file.store_line(text)
	_log_file.flush()

func _settle() -> void:
	var fs := EditorInterface.get_resource_filesystem()
	for i in 900:
		await get_tree().process_frame
		if i > 120 and not fs.is_scanning():
			return

func _do(step: Dictionary) -> String:
	match step.get("op"):
		"wait":
			for i in int(step.get("frames", 30)):
				await get_tree().process_frame
		"sleep":
			# Real time, for editor features driven by timers rather than frames.
			await get_tree().create_timer(float(step.get("seconds", 1.0))).timeout
			await _frames(5)
		"menu":
			return await _menu(step["path"])
		"open":
			var path: String = step["path"]
			if path.ends_with(".tscn") or path.ends_with(".scn"):
				EditorInterface.open_scene_from_path(path)
			else:
				EditorInterface.edit_resource(load(path))
			await _frames(30)
		"select":
			var root := EditorInterface.get_edited_scene_root()
			var node := root if step["path"] == "." else root.get_node_or_null(step["path"])
			if node == null:
				return "no node " + step["path"]
			EditorInterface.get_selection().clear()
			EditorInterface.get_selection().add_node(node)
			EditorInterface.edit_node(node)
			await _frames(20)
		"fs":
			EditorInterface.get_file_system_dock().navigate_to_path(step["path"])
			await _frames(20)
		"main_screen":
			EditorInterface.set_main_screen_editor(step["name"])
			await _frames(20)
		"capture":
			await _frames(int(step.get("frames", 20)))
			return _capture(step["name"], step.get("window", ""))
		"eval":
			var script := GDScript.new()
			# Values from the untyped plugin cannot be inferred, so ":=" on them becomes "=".
			var code := str(step["code"]).replace(":= plugin.", "= plugin.")
			script.source_code = "extends RefCounted\nfunc run(plugin, editor: EditorInterface):\n" + "\n".join(Array(code.split("\n")).map(func(l): return "\t" + l))
			if script.reload() != OK:
				return "eval did not compile"
			var result = await script.new().run(self, EditorInterface)
			await _frames(10)
			if result is String and result != "":
				return result
		"click":
			return await _click(step)
		"key":
			return await _key(step)
		"orbit":
			# Orbits the visible 3D viewport like a middle-mouse drag of dx, dy pixels.
			var orbit_view := _collect(get_tree().root, "Node3DEditorViewport", "")[0] as Control
			var at := orbit_view.get_global_transform_with_canvas() * (orbit_view.size / 2.0)
			var drag := Vector2(float(step.get("dx", 0)), float(step.get("dy", 0)))
			var press := InputEventMouseButton.new()
			press.button_index = MOUSE_BUTTON_MIDDLE
			press.button_mask = MOUSE_BUTTON_MASK_MIDDLE
			press.pressed = true
			press.position = at
			press.global_position = at
			orbit_view.get_viewport().push_input(press)
			await _frames(2)
			for i in 10:
				var motion := InputEventMouseMotion.new()
				motion.button_mask = MOUSE_BUTTON_MASK_MIDDLE
				motion.relative = drag / 10.0
				motion.screen_relative = drag / 10.0
				motion.position = at
				motion.global_position = at
				orbit_view.get_viewport().push_input(motion)
				await _frames(2)
			var release := press.duplicate() as InputEventMouseButton
			release.pressed = false
			release.button_mask = 0
			orbit_view.get_viewport().push_input(release)
			await _frames(20)
		"wheel":
			# Zooms the visible 3D viewport: positive steps zoom in.
			var view := _collect(get_tree().root, "Node3DEditorViewport", "")[0] as Control
			var center := view.get_global_transform_with_canvas() * (view.size / 2.0)
			var steps := int(step.get("steps", 1))
			for i in absi(steps):
				for pressed in [true, false]:
					var wheel := InputEventMouseButton.new()
					wheel.button_index = MOUSE_BUTTON_WHEEL_UP if steps > 0 else MOUSE_BUTTON_WHEEL_DOWN
					wheel.pressed = pressed
					wheel.factor = 1.0
					wheel.position = center
					wheel.global_position = center
					view.get_viewport().push_input(wheel)
				await _frames(3)
			await _frames(30)
		"popup":
			return await _popup(step["text"])
		"set_text":
			var edit := _find(step["find"]) as LineEdit
			if edit == null:
				return "no LineEdit"
			edit.text = step["text"]
			edit.text_changed.emit(edit.text)
			if step.get("submit", false):
				edit.text_submitted.emit(edit.text)
			await _frames(10)
		"press":
			var button := _find(step["find"]) as BaseButton
			if button == null:
				return "no button"
			button.pressed.emit()
			await _frames(30)
		"quit":
			get_tree().quit()
		_:
			return "unknown op"
	return ""

# Finds a control: inside a window by title, or by class, then narrowed by type, text, and index.
func _find(spec: Dictionary) -> Node:
	var root: Node = get_tree().root
	if spec.has("window"):
		root = null
		for window in _windows(get_tree().root):
			if window.visible and spec["window"] in window.title:
				root = window
		if root == null:
			return null
	if spec.has("class"):
		root = _find_class(root, spec["class"])
		if root == null:
			return null
	if spec.has("property"):
		root = _find_property(root, spec["property"])
		if root == null:
			return null
	if not spec.has("type") and not spec.has("text"):
		return root
	var matches := _collect(root, spec.get("type", ""), spec.get("text", ""))
	var nth := int(spec.get("nth", 0))
	if nth < 0:
		nth += matches.size()
	return matches[nth] if nth >= 0 and nth < matches.size() else null

func _collect(node: Node, type: String, text: String) -> Array:
	var found := []
	if text.begins_with("tooltip:"):
		var tooltip_matches := []
		if node is Control and node.is_visible_in_tree() and (type == "" or node.is_class(type)) and node.tooltip_text.begins_with(text.substr(8)):
			tooltip_matches.append(node)
		for child in node.get_children(true):
			tooltip_matches.append_array(_collect(child, type, text))
		return tooltip_matches
	var type_ok := type == "" or node.is_class(type)
	var text_ok := text == "" or (("text" in node) and str(node.get("text")) == text)
	if type_ok and text_ok and node is Control and node.is_visible_in_tree():
		found.append(node)
	for child in node.get_children(true):
		found.append_array(_collect(child, type, text))
	return found

func _find_class(node: Node, class_id: String) -> Node:
	if node.get_class() == class_id:
		return node
	for child in node.get_children(true):
		var found := _find_class(child, class_id)
		if found:
			return found
	return null

func _find_item(item: TreeItem, text: String) -> TreeItem:
	if item == null:
		return null
	if item.get_text(0) == text:
		return item
	for child in item.get_children():
		var found := _find_item(child, text)
		if found:
			return found
	return null

# Synthetic mouse input pushed into Godot's own viewport; the system cursor never moves.
func _click(step: Dictionary) -> String:
	var control := _find(step["find"]) as Control
	if control == null:
		return "no control for " + str(step["find"])
	var local := control.size / 2.0
	if step.has("item"):
		var tree := control as Tree if control is Tree else _collect(control, "Tree", "")[0] as Tree
		var item := _find_item(tree.get_root(), step["item"])
		if item == null:
			return "no tree item " + step["item"]
		tree.scroll_to_item(item)
		await _frames(5)
		var rect := tree.get_item_area_rect(item)
		control = tree
		local = rect.position + Vector2(min(rect.size.x / 2.0, 60.0), rect.size.y / 2.0)
	var position := control.get_global_transform_with_canvas() * local
	var button := MOUSE_BUTTON_RIGHT if step.get("button", "left") == "right" else MOUSE_BUTTON_LEFT
	var viewport := control.get_viewport()
	var motion := InputEventMouseMotion.new()
	motion.position = position
	motion.global_position = position
	viewport.push_input(motion)
	for i in (2 if step.get("double", false) else 1):
		for pressed in [true, false]:
			var event := InputEventMouseButton.new()
			event.button_index = button
			event.pressed = pressed
			event.double_click = step.get("double", false) and i == 1 and pressed
			event.position = position
			event.global_position = position
			viewport.push_input(event)
			await _frames(2)
	await _frames(20)
	return ""

func _key(step: Dictionary) -> String:
	var control := _find(step["find"]) as Control
	if control == null:
		return "no control"
	control.grab_focus()
	for pressed in [true, false]:
		var event := InputEventKey.new()
		event.keycode = OS.find_keycode_from_string(step["key"])
		event.ctrl_pressed = step.get("ctrl", false)
		event.shift_pressed = step.get("shift", false)
		event.pressed = pressed
		control.get_viewport().push_input(event)
		await _frames(2)
	await _frames(20)
	return ""

func _popup(text: String) -> String:
	for window in _windows(get_tree().root):
		if window is PopupMenu and window.visible:
			for i in window.item_count:
				if window.get_item_text(i) == text:
					window.id_pressed.emit(window.get_item_id(i))
					window.hide()
					await _frames(30)
					return ""
	return "no visible popup item " + text

func _frames(count: int) -> void:
	for i in count:
		await get_tree().process_frame

# Opens a top menu, then each submenu, and presses the last item, matching item text exactly.
func _menu(path: Array) -> String:
	var bar := _find_menu_bar(EditorInterface.get_base_control())
	if bar == null:
		return "no menu bar"
	var popup: PopupMenu = null
	for i in bar.get_menu_count():
		if bar.get_menu_title(i) == path[0]:
			popup = bar.get_menu_popup(i)
	if popup == null:
		return "no menu " + path[0]
	for depth in range(1, path.size()):
		var index := -1
		for i in popup.item_count:
			if popup.get_item_text(i) == path[depth]:
				index = i
		if index < 0:
			var items := []
			for i in popup.item_count:
				items.append(popup.get_item_text(i))
			return "no item '%s' in %s" % [path[depth], items]
		if depth < path.size() - 1:
			popup = popup.get_item_submenu_node(index)
			if popup == null:
				return "item '%s' has no submenu" % path[depth]
		else:
			popup.id_pressed.emit(popup.get_item_id(index))
			await _frames(30)
	return ""

func _find_menu_bar(node: Node) -> MenuBar:
	if node is MenuBar:
		return node
	for child in node.get_children(true):
		var found := _find_menu_bar(child)
		if found:
			return found
	return null

func _capture(name: String, window_title: String) -> String:
	var target: Viewport = get_viewport()
	if window_title != "":
		target = null
		for window in _windows(get_tree().root):
			# "class:ConfirmationDialog" picks a window by class, for dialogs without a title.
			var by_class: bool = window_title.begins_with("class:") and window.get_class() == window_title.substr(6)
			if window.visible and window != get_window() and (by_class or window_title in window.title):
				target = window
		if target == null:
			return "no visible window titled " + window_title
	var image := target.get_texture().get_image()
	image.convert(Image.FORMAT_RGBA8)
	# Native popups and dialogs are separate windows; paint the visible ones over the main window where they sit. The
	# verification editor runs in single-window mode, where they are embedded and already in the main window's image.
	if window_title == "":
		var origin := get_window().position
		for window in _windows(get_tree().root):
			if window == get_window() or not window.visible or window.is_embedded() or not (window is Popup or window is AcceptDialog or window is ConfirmationDialog):
				continue
			var shot: Image = window.get_texture().get_image()
			shot.convert(Image.FORMAT_RGBA8)
			image.blit_rect(shot, Rect2i(Vector2i.ZERO, shot.get_size()), window.position - origin)
	var error := image.save_png(_out_dir.path_join(name + ".png"))
	return "" if error == OK else "save failed %d" % error

func _windows(node: Node) -> Array:
	var found := []
	if node is Window:
		found.append(node)
	for child in node.get_children(true):
		found.append_array(_windows(child))
	return found

# The last visible inspector row editing this property (sub-inspectors nest, so the deepest match wins).
func _find_property(node: Node, property: String) -> EditorProperty:
	var found: EditorProperty = null
	if node is EditorProperty and node.get_edited_property() == property and node.is_visible_in_tree():
		found = node
	for child in node.get_children(true):
		var deeper := _find_property(child, property)
		if deeper:
			found = deeper
	return found
