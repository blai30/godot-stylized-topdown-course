# Lesson 56, in Godot: performance and exporting a build. The Debugger's Monitors, Visual Profiler, and Profiler on a running game; the
# render time of the meadow and the generated level with one cost removed at a time; then the macOS export preset, the export templates,
# an exported build, and a run of it from outside the editor.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, game_steps, open_bottom_panel, close_bottom_panel, click_tab, build

EXPORT_DIR = '../builds'
EXPORT_NAME = 'TopDownTemplate.zip'
BUNDLE = 'com.example.topdowntemplate'
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
out_dir = os.path.dirname(sys.argv[2])

REPORT = '''
var calls := Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
var objects := Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)
var primitives := Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)
var memory := Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED) / 1048576.0
var fps := Performance.get_monitor(Performance.TIME_FPS)
print("[game] {tag}: fps %d, draw calls %d, objects %d, primitives %d, video memory %.0f MB" % [fps, calls, objects, primitives, memory])
'''

# Each experiment takes one cost away, reads the frame, and puts it back.
EXPERIMENTS = [
    ('shadows off', '{root}/WorldEnvironment/Sun', 'shadow_enabled', 'false', 'true'),
    ('grass hidden', '{root}/Grass', 'visible', 'false', 'true'),
    ('trees hidden', '{root}/Trees', 'visible', 'false', 'true'),
    ('water hidden', '{root}/Water', 'visible', 'false', 'true'),
]


def experiments(root):
    steps = [
        {'op': 'eval', 'code': REPORT.format(tag=f'{root} baseline')},
    ]
    for tag, path, prop, off, on in EXPERIMENTS:
        node = path.format(root=root)
        steps += [
            {'op': 'eval', 'code': f'tree.root.get_node("{node}").{prop} = {off}'},
            {'op': 'sleep', 'seconds': 2.5},
            {'op': 'eval', 'code': REPORT.format(tag=f'{root} {tag}')},
            {'op': 'eval', 'code': f'tree.root.get_node("{node}").{prop} = {on}'},
            {'op': 'wait', 'frames': 30},
        ]
    steps += [
        {'op': 'eval', 'code': f'(tree.root.get_node("{root}/WorldEnvironment") as WorldEnvironment).environment.ssao_enabled = false'},
        {'op': 'sleep', 'seconds': 2.5},
        {'op': 'eval', 'code': REPORT.format(tag=f'{root} ambient occlusion off')},
        {'op': 'eval', 'code': f'(tree.root.get_node("{root}/WorldEnvironment") as WorldEnvironment).environment.ssao_enabled = true'},
        {'op': 'wait', 'frames': 30},
    ]
    steps += [{'op': 'eval', 'code': REPORT.format(tag=f'{root} baseline again')}]
    return steps


def measure_game(name, root, hold=False):
    return game_steps(os.path.join(out_dir, f'game-{name}.jsonl'), [
        {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
        {'op': 'eval', 'code': f'tree.root.get_node("{root}/WorldEnvironment/Day").set("Running", false)'},
        # VSync off through the pause panel's own switch, so the frame rate is the game's and not the screen's.
        {'op': 'eval', 'code': f'tree.root.get_node("{root}/WorldEnvironment/PausePanel").get_node("%VsyncToggle").button_pressed = false'},
        {'op': 'eval', 'code': 'RenderingServer.viewport_set_measure_render_time(tree.root.get_viewport_rid(), true)'},
        {'op': 'sleep', 'seconds': 3},
        *experiments(root),
        # The game stays up a while longer, so the editor can be watched while it runs.
        *([{'op': 'sleep', 'seconds': 40}] if hold else []),
        {'op': 'quit'}])


def debugger_tab(title):
    return eval_(f'''
var debugger = plugin._find_class(plugin.get_tree().root, "EditorDebuggerNode")
var titles := []
for container in debugger.find_children("*", "TabContainer", true, false):
	for i in container.get_tab_count():
		titles.append(container.get_tab_title(i))
		if container.get_tab_title(i).begins_with("{title}"):
			container.current_tab = i
			return ""
return "no debugger tab {title} in " + str(titles)
''')


def open_debugger():
    # The Debugger's tab shows how many errors it holds ("Debugger (20)"), so it is found by the start of its title.
    return eval_('''
for bar in plugin._collect(plugin.get_tree().root, "TabBar", ""):
	var titles := []
	for i in bar.tab_count:
		titles.append(bar.get_tab_title(i))
	if "Output" in titles:
		for i in titles.size():
			if titles[i].begins_with("Debugger"):
				var at: Vector2 = bar.get_global_transform_with_canvas() * bar.get_tab_rect(i).get_center()
				if bar.current_tab != i:
					for pressed in [true, false]:
						var event := InputEventMouseButton.new()
						event.button_index = MOUSE_BUTTON_LEFT
						event.pressed = pressed
						event.position = at
						event.global_position = at
						bar.get_viewport().push_input(event)
						await plugin.get_tree().process_frame
				return ""
return "no Debugger tab"
''')


def start_profiler():
    # The profiler tabs' Start buttons are toggles.
    return eval_('''
var debugger = plugin._find_class(plugin.get_tree().root, "EditorDebuggerNode")
for button in debugger.find_children("*", "Button", true, false):
	if button.is_visible_in_tree() and button.text == "Start":
		button.button_pressed = true
		return ""
return "no Start button"
''')


def tick_monitors(*names):
    return eval_(f'''
var debugger = plugin._find_class(plugin.get_tree().root, "EditorDebuggerNode")
for tree in debugger.find_children("*", "Tree", true, false):
	if not tree.is_visible_in_tree():
		continue
	var stack := [tree.get_root()]
	var found := []
	while not stack.is_empty():
		var current: TreeItem = stack.pop_back()
		if current == null:
			continue
		if {list(names)!r}.has(current.get_text(0)):
			current.set_checked(0, true)
			tree.item_edited.emit()
			found.append(current.get_text(0))
		var child := current.get_first_child()
		while child != null:
			stack.append(child)
			child = child.get_next()
	print("[probe] monitors ticked ", found)
''')


def dump_errors():
    return eval_('''
var debugger = plugin._find_class(plugin.get_tree().root, "EditorDebuggerNode")
for tree in debugger.find_children("*", "Tree", true, false):
	if not tree.is_visible_in_tree():
		continue
	var stack := [tree.get_root()]
	while not stack.is_empty():
		var current: TreeItem = stack.pop_back()
		if current == null:
			continue
		if current.get_text(0) != "" or current.get_text(1) != "":
			print("[probe] debugger row: ", current.get_text(0), " | ", current.get_text(1))
		var child := current.get_first_child()
		while child != null:
			stack.append(child)
			child = child.get_next()
''')


def run_watched(game_path, seconds, watching):
    # play(), with the editor watched while the game runs: the Debugger's tabs are captured at their moment.
    return [
        eval_('''
var log = plugin._find_class(plugin.get_tree().root, "EditorLog")
for button in log.find_children("*", "Button", true, false):
	if button.shortcut and button.shortcut.get_as_text().ends_with("K") and (button.shortcut.get_as_text().contains("Alt") or button.shortcut.get_as_text().contains("Option")):
		button.pressed.emit()
		return ""
'''),
        eval_(f'''
OS.set_environment("CAPTURE_GAME_STEPS", {game_path!r})
OS.set_environment("CAPTURE_GAME_LOG", {game_path[:-6] + '.log'!r})
DirAccess.remove_absolute({game_path[:-6] + '.log'!r})
'''),
        eval_('editor.play_current_scene()'),
        {'op': 'wait', 'frames': 40},
        *watching,
        eval_(f'''
for i in {seconds}:
	if FileAccess.get_file_as_string({game_path[:-6] + '.log'!r}).contains("[game] quit  ok"):
		return ""
	await plugin.get_tree().create_timer(1.0).timeout
return "the game's steps did not finish"
'''),
    ]


def set_row(property, value):
    return eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.get_class() == "ProjectExportDialog":
		for row in plugin._collect(window, "EditorProperty", ""):
			if str(row.get_edited_property()) == "{property}":
				row.emit_changed("{property}", {value})
				return ""
return "no row {property}"
''')


def export_dialog_button(text):
    return eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.get_class() == "ProjectExportDialog":
		for button in plugin._collect(window, "Button", ""):
			if button.text == "{text}":
				button.pressed.emit()
				return ""
return "no {text} button"
''')


def export_attempt(tag, reopen=False):
    # Export Project... with the path already in the preset: the dialog's file name is accepted, and the build waits for the zip.
    return [
        *([{'op': 'menu', 'path': ['Project', 'Export...']}, {'op': 'wait', 'frames': 60}] if reopen else []),
        eval_(f'''
OS.execute("/bin/rm", ["-f", ProjectSettings.globalize_path("res://").path_join("{EXPORT_DIR}/{EXPORT_NAME}")])
'''),
        export_dialog_button('Export Project...'),
        {'op': 'wait', 'frames': 60},
        eval_(f'''
DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://").path_join("{EXPORT_DIR}"))
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		print("[probe] export dialog at ", window.current_dir, " file ", window.current_file)
		return ""
return "no Export Project dialog"
'''),
        {'op': 'capture', 'name': tag + '_dialog'},
        eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.get_ok_button().pressed.emit()
		return ""
'''),
        {'op': 'sleep', 'seconds': 45},
        {'op': 'capture', 'name': tag + '_result'},
        eval_(f'''
var zip := ProjectSettings.globalize_path("res://").path_join("{EXPORT_DIR}/{EXPORT_NAME}")
print("[probe] {tag} zip exists ", FileAccess.file_exists(zip), " ", FileAccess.open(zip, FileAccess.READ).get_length() / 1048576.0 if FileAccess.file_exists(zip) else 0.0, " MB")
'''),
    ]


meadow = measure_game('l56_meadow', 'Meadow', True)
generated = measure_game('l56_generated', 'Generated')

steps = [
    {'op': 'sleep', 'seconds': 5},
    # The meadow, watched in the Debugger.
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    *run_watched(meadow, 150, [
        {'op': 'sleep', 'seconds': 14},
        open_debugger(),
        {'op': 'wait', 'frames': 20},
        debugger_tab('Monitors'),
        tick_monitors('FPS', 'Process', 'Total Draw Calls', 'Total Primitives'),
        {'op': 'sleep', 'seconds': 4},
        {'op': 'wait', 'frames': 40},
        {'op': 'capture', 'name': 'l56_monitors'},
        debugger_tab('Visual Profiler'),
        {'op': 'wait', 'frames': 40},
        {'op': 'capture', 'name': 'l56_visual_profiler_idle'},
        start_profiler(),
        {'op': 'sleep', 'seconds': 5},
        {'op': 'capture', 'name': 'l56_visual_profiler'},
        debugger_tab('Profiler'),
        {'op': 'wait', 'frames': 40},
        start_profiler(),
        {'op': 'sleep', 'seconds': 5},
        {'op': 'capture', 'name': 'l56_profiler'},

    ]),
    close_bottom_panel(),
    # The generated level.
    click_tab('Scene'),
    {'op': 'open', 'path': 'res://levels/generated.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    *run_watched(generated, 150, []),
    # The export dialog and the templates.
    eval_('EditorInterface.get_editor_settings().set_setting("network/connection/network_mode", 1)'),
    {'op': 'menu', 'path': ['Project', 'Export...']},
    {'op': 'wait', 'frames': 60},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.get_class() == "ProjectExportDialog":
		for menu in plugin._collect(window, "MenuButton", ""):
			var popup: PopupMenu = menu.get_popup()
			for i in popup.item_count:
				if popup.get_item_text(i) == "macOS":
					popup.index_pressed.emit(i)
					return ""
return "no macOS in the Add menu"
'''),
    {'op': 'wait', 'frames': 60},
    {'op': 'capture', 'name': 'l56_preset', 'window': 'Export'},
    set_row('application/bundle_identifier', f'"{BUNDLE}"'),
    set_row('codesign/codesign', '0'),
    set_row('export_path', f'"{EXPORT_DIR}/{EXPORT_NAME}"'),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l56_preset_set', 'window': 'Export'},
    eval_('''
var templates := EditorInterface.get_editor_paths().get_data_dir().path_join("export_templates/4.8.beta1.mono/macos.zip")
print("[probe] template present ", FileAccess.file_exists(templates))
'''),
    *export_attempt('l56_first'),
    # The export fails: two editor-only scripts cannot be built into a game.
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window.get_class() == "ProjectExportDialog":
		window.hide()
'''),
    {'op': 'wait', 'frames': 30},
    open_bottom_panel('MSBuild'),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l56_msbuild'},
    eval_('''
var logs := EditorInterface.get_editor_paths().get_data_dir().path_join("mono/build_logs")
for folder in DirAccess.get_directories_at(logs):
	var issues := logs.path_join(folder).path_join("msbuild_issues.csv")
	if folder.contains("Export") and FileAccess.file_exists(issues):
		print("[probe] export build issues in ", folder, ": ", FileAccess.get_file_as_string(issues))
'''),
    # The fix: the two tools are wrapped in #if TOOLS.
    eval_('''
for path in ["res://src/Tools/BuildDay.cs", "res://src/Tools/GrassDetail.cs"]:
	var text := FileAccess.get_file_as_string(path).rstrip("\\n")
	var file := FileAccess.open(path, FileAccess.WRITE)
	file.store_string("#if TOOLS\\n" + text + "\\n#endif\\n")
	file.close()
'''),
    *build('l56_built'),
    *export_attempt('l56_second', True),
    {'op': 'wait', 'frames': 60},
    {'op': 'capture', 'name': 'l56_exported'},
    # The build, run from outside the editor.
    eval_(f'''
var builds := ProjectSettings.globalize_path("res://").path_join("{EXPORT_DIR}").simplify_path()
var run := builds.path_join("run")
OS.execute("/bin/rm", ["-rf", run])
DirAccess.make_dir_recursive_absolute(run)
var output := []
var code := OS.execute("/usr/bin/ditto", ["-x", "-k", builds.path_join("{EXPORT_NAME}"), run], output, true)
print("[probe] unzip exit ", code, " ", output)
var listing := []
OS.execute("/bin/ls", ["-R", run.path_join("TopDownTemplate.app/Contents/Resources")], listing, true)
print("[probe] resources ", listing)
var started := Time.get_ticks_msec()
var log := []
var run_code := OS.execute(run.path_join("TopDownTemplate.app/Contents/MacOS/TopDownTemplate"), ["--quit-after", "600"], log, true)
print("[probe] exported game exit ", run_code, " after ", (Time.get_ticks_msec() - started) / 1000.0, " s")
var errors := []
for line in "".join(log).split("\\n"):
	# The test project's capture driver is not part of a reader's project, so its own message is not counted.
	if line.contains("ERROR") and not line.contains(".capture") and not line.contains("autoload") and not line.contains("resource_loader") and not line.contains("gdscript.cpp"):
		errors.append(line)
print("[probe] exported game errors ", errors.size(), " ", errors.slice(0, 5))
print("[probe] exported game output ", "".join(log).left(800))
'''),
    {'op': 'quit'},
]
write(sys.argv[2], steps)
