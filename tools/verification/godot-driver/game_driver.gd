extends Node

# Replays the steps in the JSON file named by the CAPTURE_GAME_STEPS environment variable inside the running game,
# one per line. Events go through Input.parse_input_event, so they reach the game's input map and _UnhandledInput
# exactly as real input does, and the system mouse and keyboard are never touched.
#   {"op": "wait", "frames": 60}
#   {"op": "sleep", "seconds": 1.0}
#   {"op": "wheel", "steps": 3}                 positive steps scroll up (zoom_in), negative down
#   {"op": "key", "key": "W", "pressed": true}   presses or releases a key by its physical position
#   {"op": "capture", "name": "file"}
#   {"op": "eval", "code": "..."}               runs GDScript with `tree` bound; print(...) lines are logged
#   {"op": "quit"}
# The game's own window size is used for captures. Every step logs "[game] <op> ok" or "[game] <op> FAILED: <reason>"
# to the CAPTURE_GAME_LOG file.

func _ready() -> void:
	var steps_path := OS.get_environment("CAPTURE_GAME_STEPS")
	if steps_path == "" or Engine.is_editor_hint():
		return
	_run.call_deferred(steps_path)

func _run(steps_path: String) -> void:
	var out_dir := OS.get_environment("CAPTURE_OUT")
	for line in FileAccess.get_file_as_string(steps_path).split("\n", false):
		var step: Dictionary = JSON.parse_string(line)
		var error: String = await _do(step, out_dir)
		_log("[game] %s %s%s" % [step.get("op"), step.get("name", ""), " ok" if error == "" else " FAILED: " + error])
		if error != "":
			break
	get_tree().quit()

# Results go to the file named by CAPTURE_GAME_LOG, not the Output panel, so they never show in captures of it.
func _log(text: String) -> void:
	var path := OS.get_environment("CAPTURE_GAME_LOG")
	var file := FileAccess.open(path, FileAccess.READ_WRITE if FileAccess.file_exists(path) else FileAccess.WRITE)
	file.seek_end()
	file.store_line(text)
	file.close()

func _do(step: Dictionary, out_dir: String) -> String:
	match step.get("op"):
		"wait":
			for i in int(step.get("frames", 30)):
				await get_tree().process_frame
		"sleep":
			await get_tree().create_timer(float(step.get("seconds", 1.0))).timeout
		"wheel":
			var steps := int(step.get("steps", 1))
			var center := get_viewport().get_visible_rect().size / 2.0
			for i in absi(steps):
				for pressed in [true, false]:
					var wheel := InputEventMouseButton.new()
					wheel.button_index = MOUSE_BUTTON_WHEEL_UP if steps > 0 else MOUSE_BUTTON_WHEEL_DOWN
					wheel.pressed = pressed
					wheel.factor = 1.0
					wheel.position = center
					wheel.global_position = center
					Input.parse_input_event(wheel)
				await get_tree().process_frame
				await get_tree().process_frame
		"key":
			var key := InputEventKey.new()
			key.physical_keycode = OS.find_keycode_from_string(step["key"])
			key.keycode = key.physical_keycode
			key.pressed = step.get("pressed", true)
			Input.parse_input_event(key)
		"capture":
			for i in int(step.get("frames", 5)):
				await get_tree().process_frame
			var image := get_viewport().get_texture().get_image()
			if image.save_png(out_dir.path_join(step["name"] + ".png")) != OK:
				return "save failed"
		"eval":
			var script := GDScript.new()
			# Lines starting with print( go to the log file instead, like the steps' own results.
			var lines := Array(str(step["code"]).split("\n")).map(func(l: String): return "\t" + ("write_log.call(str(" + l.substr(6) + ")" if l.begins_with("print(") else l))
			script.source_code = "extends RefCounted\nfunc run(tree: SceneTree, write_log: Callable):\n" + "\n".join(lines)
			if script.reload() != OK:
				return "eval did not compile"
			var result = await script.new().run(get_tree(), _log)
			if result is String and result != "":
				return result
		"quit":
			get_tree().quit()
		_:
			return "unknown op"
	return ""
