# Lesson 22: DayClock. A script on the Day player that sets the day animation from a time of day, lets it run at a day
# length and speed, and prints the hour. Checked at dawn, dusk, and moonlight in the game.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, inspector_set, unfold_inspector, show_row, make_folder, save_code, build, game_steps, play,
                   dump_windows, close_bottom_panel)

SCENE = 'res://world/environment/world_environment.tscn'
SCRIPT = 'res://src/World/DayClock.cs'
SCENE_TREE = {'class': 'SceneTreeDock', 'type': 'Tree'}
SAVE_SCENE = {'op': 'key', 'find': SCENE_TREE, 'key': 'S', 'ctrl': True}
CLOCK = 'Meadow/WorldEnvironment/Day'

PIECES = ['''using Godot;

namespace TopDownTemplate.World;

// Drives the day animation from a time of day, so a slider, a save file, or a cutscene can set the hour.
[Tool]
public partial class DayClock : AnimationPlayer
{
	private static readonly StringName DayAnimation = "day";

	private float _timeOfDay = 0.5f;
	private int _hour = -1;

	// The time of day from 0 (midnight) to 1, with noon at 0.5.
	[Export(PropertyHint.Range, "0,1,0.001")]
	public float TimeOfDay
	{
		get => _timeOfDay;
		set
		{
			_timeOfDay = Mathf.PosMod(value, 1f);
			Apply();
		}
	}

	// How many real seconds a whole day takes at Speed 1.
	[Export] public float DayLengthSeconds { get; set; } = 600f;

	// A multiplier on how fast the day passes.
	[Export] public float Speed { get; set; } = 1f;

	// Whether the day passes at all. Turn it off to hold one hour.
	[Export] public bool Running { get; set; } = true;

	public override void _Ready()
	{
		Apply();
	}

	public override void _Process(double delta)
	{
		if (Engine.IsEditorHint() || !Running)
		{
			return;
		}

		TimeOfDay += (float)delta * Speed / DayLengthSeconds;
		PrintHour();
	}

	// Puts every animated property where the day animation has it at the current time of day.
	private void Apply()
	{
		if (!IsInsideTree() || !HasAnimation(DayAnimation))
		{
			return;
		}

		AssignedAnimation = DayAnimation;
		Seek(_timeOfDay * GetAnimation(DayAnimation).Length, true);
	}

	private void PrintHour()
	{
		var hour = (int)(_timeOfDay * 24f);
		if (hour == _hour)
		{
			return;
		}

		_hour = hour;
		GD.Print($"{hour:00}:00");
	}
}
''']


def clock_eval(code):
    return {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}") as AnimationPlayer\n' + code}


def report(label):
    return {'op': 'eval', 'code': f'''var clock := tree.root.get_node("{CLOCK}")
var sun := tree.root.get_node("Meadow/WorldEnvironment/Sun") as DirectionalLight3D
print("[game] {label} time ", snappedf(clock.get("TimeOfDay"), 0.0001), " sun ", sun.light_color.to_html(false), " ", snappedf(sun.light_energy, 0.001), " ", sun.rotation_degrees.snapped(Vector3.ONE * 0.1))'''}


def set_time(value):
    return clock_eval(f'clock.set("TimeOfDay", {value})')


# Held hours: the clock stops, the hour is set, and the game captures it.
held = [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    report('start'),
    {'op': 'capture', 'name': 'l22_start', 'frames': 10},
    clock_eval('clock.set("Running", false)'),
]
for time, name in ((0.0, 'midnight'), (0.1499, 'before swap'), (0.1501, 'after swap'), (0.2, 'dawn'), (0.5, 'noon'),
                   (0.8, 'dusk'), (0.8499, 'before sunset swap'), (0.8501, 'after sunset swap'), (0.95, 'moon')):
    held += [set_time(time), {'op': 'wait', 'frames': 40}, report(name)]
    if name in ('dawn', 'dusk', 'moon', 'noon'):
        held += [{'op': 'capture', 'name': f'l22_{name}', 'frames': 10}]
held += [{'op': 'quit'}]
held_path = game_steps(os.path.join(os.environ['TEMP'], 'sgt-phase1', 'game-l22-held.jsonl'), held)

# A short day: 12 seconds, so the hours print quickly.
fast_path = game_steps(os.path.join(os.environ['TEMP'], 'sgt-phase1', 'game-l22-fast.jsonl'), [
    {'op': 'wait', 'frames': 30},
    clock_eval('clock.set("DayLengthSeconds", 12.0)\nclock.set("TimeOfDay", 0.7)'),
    {'op': 'sleep', 'seconds': 5},
    report('running'),
    {'op': 'quit'},
])

steps = [
    {'op': 'sleep', 'seconds': 3},
    *make_folder('src', 'World'),
    {'op': 'open', 'path': SCENE},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    {'op': 'select', 'path': 'Day'},
    {'op': 'wait', 'frames': 30},
    {'op': 'press', 'find': {'class': 'SceneTreeDock', 'type': 'Button', 'text': 'tooltip:Attach a new or existing script'}},
    {'op': 'wait', 'frames': 40},
    eval_(f'''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is ScriptCreateDialog:
		var language: OptionButton = plugin._collect(window, "OptionButton", "")[0]
		for i in language.item_count:
			if language.get_item_text(i) == "C#":
				language.select(i)
				language.item_selected.emit(i)
		await plugin.get_tree().process_frame
		var path: LineEdit = null
		for edit in plugin._collect(window, "LineEdit", ""):
			if str(edit.text).begins_with("res://"):
				path = edit
		var template: OptionButton = plugin._collect(window, "OptionButton", "")[1]
		var items := []
		for i in template.item_count:
			items.append(template.get_item_text(i))
		print("[probe] templates ", items, " selected ", template.get_item_text(template.selected))
		for i in template.item_count:
			if template.get_item_text(i) == "Node: Default":
				template.select(i)
				template.item_selected.emit(i)
		path.text = "{SCRIPT}"
		path.text_changed.emit(path.text)
		return ""
return "no Attach Node Script dialog"
'''),
    {'op': 'wait', 'frames': 30},
    dump_windows(),
    {'op': 'capture', 'name': 'l22_attach_script', 'window': 'Attach Node Script'},
    {'op': 'press', 'find': {'window': 'Attach Node Script', 'type': 'Button', 'text': 'Create'}},
    {'op': 'wait', 'frames': 60},
    eval_(f'print("[probe] template class line ", Array(FileAccess.get_file_as_string("{SCRIPT}").split("\\n")).filter(func(l): return l.contains("class")))'),
    save_code(SCRIPT, PIECES[0]),
    *build(),
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 40},
    {'op': 'select', 'path': 'Day'},
    unfold_inspector(),
    {'op': 'wait', 'frames': 30},
    # Autoplay off: the clock sets the time now.
    {'op': 'press', 'find': {'class': 'AnimationPlayerEditor', 'type': 'Button', 'text': 'tooltip:Autoplay on Load'}},
    {'op': 'wait', 'frames': 20},
    show_row('TimeOfDay'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l22_exports', 'frames': 20},
    eval_('''
var player := editor.get_edited_scene_root().get_node("Day") as AnimationPlayer
print("[probe] autoplay '", player.autoplay, "' time ", player.get("TimeOfDay"), " length ", player.get("DayLengthSeconds"), " speed ", player.get("Speed"), " running ", player.get("Running"))
'''),
    # The slider in the editor.
    inspector_set('TimeOfDay', '0.8'),
    {'op': 'wait', 'frames': 40},
    close_bottom_panel(),
    {'op': 'wait', 'frames': 40},
    {'op': 'capture', 'name': 'l22_editor_dusk', 'frames': 20},
    eval_('''
var root := editor.get_edited_scene_root() as WorldEnvironment
print("[probe] editor at 0.8 sun ", (root.get_node("Sun") as DirectionalLight3D).light_energy, " fog ", root.environment.fog_light_color.to_html(false))
'''),
    inspector_set('TimeOfDay', '0.5'),
    {'op': 'wait', 'frames': 40},
    SAVE_SCENE,
    {'op': 'wait', 'frames': 40},
    eval_('''
var scene = load("res://world/environment/world_environment.tscn").instantiate()
print("[probe] saved time ", scene.get("TimeOfDay"), " autoplay '", scene.get_node("Day").autoplay, "' sun ", scene.get_node("Sun").light_energy, " ambient ", scene.environment.background_energy_multiplier)
'''),
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'wait', 'frames': 40},
    *play(held_path, 60),
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'wait', 'frames': 40},
    *play(fast_path, 20, capture_output='l22_output'),
]
write(sys.argv[2], steps)
