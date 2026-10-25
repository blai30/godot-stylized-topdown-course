# Lesson 18: ground tiles as custom resources. GroundTile and GroundTileSet are Resource scripts made in the Script
# editor, GroundMap is attached to the meadow's GridMap, the three tiles are filled in the Inspector and saved as one
# file, and the player multiplies its speed by the tile under it.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, inspector_set, unfold_inspector, show_row, resource_menu, open_resource, save_code,
                   build, open_in_file_dialog, make_folder, dump_windows, game_steps, play, new_script, INSPECTOR)

PIECES = [
    'using Godot;\n\nnamespace TopDownTemplate.Ground;\n\n// What one kind of ground means to the game.\n[GlobalClass]\npublic partial class GroundTile : Resource\n{\n\t[Export] public string DisplayName { get; set; } = "";\n\n\t// The tile\'s number in the MeshLibrary.\n\t[Export] public int Item { get; set; }\n\n\t// Which layer the ground sits on, from the lowest at 0.\n\t[Export] public int Layer { get; set; }\n\n\t// How thickly grass grows here, from 0 to 1.\n\t[Export(PropertyHint.Range, "0,1,0.05")] public float GrassDensity { get; set; }\n\n\t// How fast the player walks here, as a share of normal speed.\n\t[Export(PropertyHint.Range, "0,2,0.05")] public float WalkSpeed { get; set; } = 1f;\n}\n',
    'using Godot;\nusing Godot.Collections;\n\nnamespace TopDownTemplate.Ground;\n\n// Every kind of ground in the game.\n[GlobalClass]\npublic partial class GroundTileSet : Resource\n{\n\t[Export] public Array<GroundTile> Tiles { get; set; } = [];\n\n\t// Finds the tile for a MeshLibrary item number.\n\tpublic GroundTile? Find(int item)\n\t{\n\t\tforeach (var tile in Tiles)\n\t\t{\n\t\t\tif (tile.Item == item)\n\t\t\t{\n\t\t\t\treturn tile;\n\t\t\t}\n\t\t}\n\n\t\treturn null;\n\t}\n}\n',
    'using Godot;\n\nnamespace TopDownTemplate.Ground;\n\n// The painted ground, which can say what kind of ground lies at a point.\npublic partial class GroundMap : GridMap\n{\n\t[Export] public GroundTileSet? Tiles { get; set; }\n\n\t// The ground under a point in the world, or null where nothing is painted.\n\tpublic GroundTile? TileAt(Vector3 worldPosition)\n\t{\n\t\tvar local = ToLocal(worldPosition);\n\t\tlocal.Y = 0f;\n\t\tvar item = GetCellItem(LocalToMap(local));\n\t\treturn item == InvalidCellItem ? null : Tiles?.Find(item);\n\t}\n}\n',
    'using Godot;\nusing TopDownTemplate.Ground;\n\nnamespace TopDownTemplate.Player;\n\n// Walks the player with the move actions and turns it to face where it walks.\npublic partial class PlayerMovement : CharacterBody3D\n{\n\tprivate static readonly StringName MoveLeft = "move_left";\n\tprivate static readonly StringName MoveRight = "move_right";\n\tprivate static readonly StringName MoveForward = "move_forward";\n\tprivate static readonly StringName MoveBack = "move_back";\n\tprivate static readonly StringName Sprint = "sprint";\n\n\t[Export] public float Speed { get; set; } = 3.5f;\n\t[Export] public float SprintSpeed { get; set; } = 6f;\n\n\t// How quickly the player speeds up and slows down, in meters per second, per second.\n\t[Export] public float Acceleration { get; set; } = 30f;\n\n\t// The ground to walk on, which sets how fast each kind of ground lets the player go.\n\t[Export] public GroundMap? Ground { get; set; }\n\n\tpublic override void _PhysicsProcess(double delta)\n\t{\n\t\tvar step = (float)delta;\n\t\tvar input = Input.GetVector(MoveLeft, MoveRight, MoveForward, MoveBack);\n\t\tvar speed = Input.IsActionPressed(Sprint) ? SprintSpeed : Speed;\n\t\tspeed *= Ground?.TileAt(GlobalPosition)?.WalkSpeed ?? 1f;\n\t\tvar target = new Vector3(input.X, 0f, input.Y) * speed;\n\n\t\tvar velocity = Velocity;\n\t\tvar horizontal = new Vector3(velocity.X, 0f, velocity.Z).MoveToward(target, Acceleration * step);\n\t\tvelocity.X = horizontal.X;\n\t\tvelocity.Z = horizontal.Z;\n\t\tif (!IsOnFloor())\n\t\t{\n\t\t\tvelocity += GetGravity() * step;\n\t\t}\n\n\t\tVelocity = velocity;\n\t\tMoveAndSlide();\n\n\t\tif (target != Vector3.Zero)\n\t\t{\n\t\t\t// Turns the player\'s front, +Z, toward where it walks.\n\t\t\tLookAt(GlobalPosition + target, Vector3.Up, true);\n\t\t}\n\t}\n}\n',
]
TILE, TILE_SET, MAP, PLAYER = 'res://src/Ground/GroundTile.cs', 'res://src/Ground/GroundTileSet.cs', 'res://src/Ground/GroundMap.cs', 'res://src/Player/PlayerMovement.cs'


steps = [
    {'op': 'sleep', 'seconds': 3},
    *make_folder('src', 'Ground'),
    {'op': 'fs', 'path': 'res://src/Ground'},
    *new_script(TILE, 'Resource', 'l18_new_script'),
    eval_(f'print("[probe] template\\n", FileAccess.get_file_as_string("{TILE}"))'),
    save_code(TILE, PIECES[0]),
    *new_script(TILE_SET, 'Resource'),
    save_code(TILE_SET, PIECES[1]),
    *build('l18_built_piece2'),
    eval_('''
var names := []
for entry in ProjectSettings.get_global_class_list():
	names.append(entry["class"])
print("[probe] global classes ", names)
if not names.has("GroundTile") or not names.has("GroundTileSet"):
	return "the resource classes are not registered"
'''),
    # Attach the map script to the meadow's GridMap.
    {'op': 'open', 'path': 'res://levels/meadow.tscn'},
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 30},
    {'op': 'select', 'path': 'GroundTiles'},
    {'op': 'press', 'find': {'class': 'SceneTreeDock', 'type': 'Button', 'text': 'tooltip:Attach a new or existing script'}},
    {'op': 'wait', 'frames': 40},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is ScriptCreateDialog:
		var language: OptionButton = plugin._collect(window, "OptionButton", "")[0]
		for i in language.item_count:
			if language.get_item_text(i) == "C#":
				language.select(i)
				language.item_selected.emit(i)
		await plugin.get_tree().process_frame
		for edit in plugin._collect(window, "LineEdit", ""):
			if str(edit.text).begins_with("res://"):
				print("[probe] default script path ", edit.text)
				edit.text = "res://src/Ground/GroundMap.cs"
				edit.text_changed.emit(edit.text)
'''),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l18_attach_map', 'window': 'Attach Node Script'},
    {'op': 'press', 'find': {'window': 'Attach Node Script', 'type': 'Button', 'text': 'Create'}},
    {'op': 'wait', 'frames': 60},
    save_code(MAP, PIECES[2]),
    *build('l18_built_piece3'),
    {'op': 'select', 'path': 'GroundTiles'},
    {'op': 'wait', 'frames': 30},
    eval_('''
for property in plugin._collect(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "EditorProperty", ""):
	print("[probe] row ", property.get_edited_property(), " label ", property.label, " ", property.get_class())
'''),
    {'op': 'capture', 'name': 'l18_tiles_empty', 'frames': 20},
    resource_menu('Tiles', 'GroundTileSet'),
    {'op': 'wait', 'frames': 30},
    open_resource('Tiles', 'Tiles'),
    unfold_inspector(),
    {'op': 'wait', 'frames': 30},
    eval_('''
var library := load("res://art/ground/ground_tiles.meshlib") as MeshLibrary
var out := []
for id in library.get_item_list():
	out.append("%d %s" % [id, library.get_item_name(id)])
print("[probe] mesh library items ", out)
'''),
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l18_set_open', 'frames': 20},
    # The array's own button opens its elements.
    eval_('''
var rows := plugin._collect(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "EditorPropertyArray", "")
print("[probe] array rows ", rows.size())
for button in plugin._collect(rows[0], "Button", ""):
	print("[probe] array button ", button.text)
var toggle: Button = plugin._collect(rows[0], "Button", "")[0]
print("[probe] toggle mode ", toggle.toggle_mode)
toggle.button_pressed = true
toggle.toggled.emit(true)
toggle.pressed.emit()
await plugin.get_tree().process_frame
await plugin.get_tree().process_frame
for property in plugin._collect(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "Control", ""):
	if property.get_class().begins_with("EditorProperty") or property.get_class().begins_with("EditorSpin"):
		print("[probe] after open ", property.get_class(), " ", property.get("label") if "label" in property else "", " ", property.get_edited_property() if property is EditorProperty else "")
'''),
    {'op': 'wait', 'frames': 20},
    eval_('''
var rows := plugin._collect(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "EditorPropertyArray", "")
var slider: EditorSpinSlider = plugin._collect(rows[0], "EditorSpinSlider", "")[0]
slider.value = 3
slider.value_changed.emit(3)
for attempt in 20:
	await plugin.get_tree().process_frame
'''),
    {'op': 'wait', 'frames': 20},
]
TILES = [('Grass', 0, 2, 1.0, 1.0), ('Sand', 1, 0, 0.0, 0.7), ('Dirt', 2, 1, 0.1, 1.15)]
for index, (name, item, layer, density, speed) in enumerate(TILES):
    row = f'indices/{index}'
    steps += [
        resource_menu(row, 'GroundTile'),
        {'op': 'wait', 'frames': 20},
        # An element's name button opens the tile in place, below its row; the rows of the newest tile come last.
        eval_(f'''
var row = plugin._find_property(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "{row}")
var picker = plugin._collect(row, "EditorResourcePicker", "")[0]
for button in plugin._collect(picker, "Button", ""):
	if str(button.text).begins_with("GroundTile"):
		button.pressed.emit()
		for attempt in 30:
			await plugin.get_tree().process_frame
		return ""
return "no GroundTile button in {row}"
'''),
        unfold_inspector(),
        {'op': 'wait', 'frames': 20},
        inspector_set('DisplayName', f'"{name}"'),
        inspector_set('Item', str(item)),
        inspector_set('Layer', str(layer)),
        inspector_set('GrassDensity', str(density)),
        inspector_set('WalkSpeed', str(speed)),
        {'op': 'wait', 'frames': 20},
    ]
steps += [
    {'op': 'capture', 'name': 'l18_tiles_filled', 'frames': 20},
    eval_('''
var tiles = editor.get_edited_scene_root().get_node("GroundTiles").get("Tiles")
var expected := [["Grass", 0, 2, 1.0, 1.0], ["Sand", 1, 0, 0.0, 0.7], ["Dirt", 2, 1, 0.1, 1.15]]
var list = tiles.get("Tiles")
if list.size() != 3:
	return "the set has %d tiles" % list.size()
for i in 3:
	var tile = list[i]
	var got := [tile.get("DisplayName"), tile.get("Item"), tile.get("Layer"), snappedf(tile.get("GrassDensity"), 0.001), snappedf(tile.get("WalkSpeed"), 0.001)]
	print("[probe] tile ", got)
	if str(got) != str(expected[i]):
		return "tile %d is %s, not %s" % [i, got, expected[i]]
'''),
    # Save the set as its own file: the Tiles row of the map, not the array row inside the set.
    eval_('''
var rows := []
for property in plugin._collect(plugin._find_class(plugin.get_tree().root, "InspectorDock"), "EditorPropertyResource", ""):
	if property.get_edited_property() == "Tiles":
		rows.append(property)
var row = rows[0]
editor.get_inspector().ensure_control_visible(row)
for button in plugin._collect(row, "Button", ""):
	button.pressed.emit()
	for attempt in 10:
		await plugin.get_tree().process_frame
		for window in plugin._windows(plugin.get_tree().root):
			if window is PopupMenu and window.visible:
				for i in window.item_count:
					if window.get_item_text(i) == "Save As...":
						window.id_pressed.emit(window.get_item_id(i))
						window.hide()
						return ""
				window.hide()
return "no Save As... in the Tiles menu"
'''),
    {'op': 'wait', 'frames': 30},
    open_in_file_dialog('art', 'ground'),
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.current_file = "ground_tile_set.tres"
		return ""
return "no Save Resource dialog"
'''),
    {'op': 'capture', 'name': 'l18_save_set', 'window': 'class:EditorFileDialog'},
    eval_('''
for window in plugin._windows(plugin.get_tree().root):
	if window.visible and window is EditorFileDialog:
		window.get_ok_button().pressed.emit()
		return ""
'''),
    {'op': 'wait', 'frames': 40},
    eval_('''
var set = load("res://art/ground/ground_tile_set.tres")
print("[probe] saved set ", set.get("Tiles").size(), " tiles")
if set.get("Tiles").size() != 3:
	return "the saved set does not hold three tiles"
'''),
    {'op': 'key', 'find': {'class': 'SceneTreeDock', 'type': 'Tree'}, 'key': 'S', 'ctrl': True},
    {'op': 'wait', 'frames': 30},
    # The player reads the tile under it.
    save_code(PLAYER, PIECES[3]),
    *build('l18_built_piece4'),
    {'op': 'select', 'path': 'Player'},
    {'op': 'wait', 'frames': 30},
    {'op': 'press', 'find': {**INSPECTOR, 'property': 'Ground', 'type': 'Button', 'text': 'Assign...'}},
    {'op': 'wait', 'frames': 40},
    {'op': 'click', 'find': {'window': 'Select a Node', 'type': 'Tree'}, 'item': 'GroundTiles'},
    {'op': 'capture', 'name': 'l18_select_ground', 'window': 'Select a Node'},
    {'op': 'press', 'find': {'window': 'Select a Node', 'type': 'Button', 'text': 'OK'}},
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l18_ground_assigned', 'frames': 20},
    {'op': 'key', 'find': {'class': 'SceneTreeDock', 'type': 'Tree'}, 'key': 'S', 'ctrl': True},
    {'op': 'wait', 'frames': 30},
]


def probe(label, key, x, z):
    # Puts the player on a kind of ground, walks it for a moment, and reports the tile under it and its speed.
    return [
        {'op': 'eval', 'code': f'''var player := tree.root.get_node("Meadow/Player") as CharacterBody3D
player.global_position = Vector3({x}, 0.05, {z})
player.velocity = Vector3.ZERO'''},
        {'op': 'wait', 'frames': 20},
        {'op': 'key', 'key': key, 'pressed': True},
        {'op': 'sleep', 'seconds': 0.3},
        {'op': 'eval', 'code': f'''var player := tree.root.get_node("Meadow/Player") as CharacterBody3D
var ground := tree.root.get_node("Meadow/GroundTiles")
var tile = ground.call("TileAt", player.global_position)
print("[game] {label} tile ", tile.get("DisplayName") if tile else "none", " speed ", snappedf(Vector2(player.velocity.x, player.velocity.z).length(), 0.01))'''},
        {'op': 'key', 'key': key, 'pressed': False},
        {'op': 'wait', 'frames': 20},
    ]


game = game_steps(os.path.join(os.environ['TEMP'], 'sgt-phase1', 'game-l18.jsonl'), [
    {'op': 'wait', 'frames': 60},
    {'op': 'sleep', 'seconds': 4},
    *probe('grass', 'W', -5, -3),
    *probe('dirt', 'S', -9.75, 1.9),
    *probe('sand', 'W', -7, -5.8),
    {'op': 'wheel', 'steps': 4},
    {'op': 'capture', 'name': 'l18_game', 'frames': 10},
    {'op': 'quit'},
])
steps += play(game, 25)
write(sys.argv[2], steps)
