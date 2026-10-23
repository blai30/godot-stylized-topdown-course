extends SceneTree

# Writes project.godot the way the 4.8 beta1 Project Manager does (editor/project_manager/project_dialog.cpp and
# EditorNode::get_initial_settings at 4d10419ca), for a Forward+ project.
func _init() -> void:
	var args := OS.get_cmdline_user_args()
	var path: String = args[0]
	var name: String = args[1]
	var features := ProjectSettings.get_setting("application/config/features") as PackedStringArray
	var settings := {
		"rendering/renderer/rendering_method": "forward_plus",
		"application/config/features": PackedStringArray(["%d.%d" % [Engine.get_version_info()["major"], Engine.get_version_info()["minor"]], "Forward Plus"]),
		"application/config/name": name,
		"application/config/icon": "res://icon.svg",
		"display/window/stretch/aspect": "expand",
		"display/window/stretch/mode": "canvas_items",
		"gui/common/auto_focus_strategy": 1,
		"input_devices/joypads/ignore_joypad_on_unfocused_application": true,
		"physics/3d/physics_engine": "Jolt Physics",
		"rendering/rendering_device/driver.windows": "d3d12",
		"rendering/lights_and_shadows/multi_bounce_occlusion/enabled": true,
	}
	for key in settings:
		ProjectSettings.set_setting(key, settings[key])
	print("features before: ", features, " save: ", ProjectSettings.save_custom(path.path_join("project.godot")))
	quit()
