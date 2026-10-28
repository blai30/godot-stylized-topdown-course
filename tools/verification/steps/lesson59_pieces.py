# The code and text of lesson 59, shared by the step script and the page's checkpoint.

AUDIT = r'''@tool
extends EditorScript

# Checks the project against its rules. Open it in the Script editor and choose File > Run: the Output panel lists every
# rule that is broken, or says there are no problems.
#
# 1. The art folder is a library: no scripts, and no path that leaves the folder.
# 2. Files and folders outside src/ are snake_case, and files and folders in src/ are PascalCase.

const ART := "res://art"
const SOURCE := "res://src"
# Folders that are not the project's own to name: Godot's cache, the build output, and the art's source files.
const SKIPPED := ["res://.godot", "res://builds", "res://art_source", "res://.git", "res://.idea", "res://.vscode", "res://bin", "res://obj"]
# Files in the project root that keep the name their tool gives them: the project's own name, and dotfiles.
const ROOT_EXTENSIONS := ["csproj", "sln"]
const TEXT_EXTENSIONS := ["tscn", "tres", "gdshader", "gdshaderinc"]
# Files from other authors keep the names they came with.
const VENDOR_FILES := ["res://art/animations/UAL1_Standard.glb"]
const SNAKE_CASE := "^[a-z0-9]+(_[a-z0-9]+)*$"
const PASCAL_CASE := "^[A-Z][A-Za-z0-9]*$"

var _problems: Array[String] = []


func _run() -> void:
	var paths := _files("res://")
	for path in paths:
		if path.begins_with(ART + "/"):
			_check_art_file(path)
		_check_name(path)
	for problem in _problems:
		print(problem)
	print("Audited %d files: %d problems." % [paths.size(), _problems.size()])


# Every file under a folder, skipping the folders that are not the project's own.
func _files(folder: String) -> Array[String]:
	var found: Array[String] = []
	for entry in DirAccess.get_files_at(folder):
		found.append(folder.path_join(entry))
	for entry in DirAccess.get_directories_at(folder):
		var path := folder.path_join(entry)
		if not SKIPPED.has(path):
			found.append_array(_files(path))
	return found


func _check_art_file(path: String) -> void:
	var extension := path.get_extension()
	if extension == "cs" or extension == "gd":
		_problems.append("%s: the art folder holds no scripts." % path)
		return
	if not TEXT_EXTENSIONS.has(extension):
		return
	var text := FileAccess.get_file_as_string(path)
	var outside := RegEx.create_from_string("res://[^\"'\\s)\\]]+")
	for found in outside.search_all(text):
		var target := found.get_string()
		if not target.begins_with(ART + "/"):
			_problems.append("%s: points outside the art folder, to %s." % [path, target])
	if text.contains("type=\"Script\""):
		_problems.append("%s: uses a script." % path)


# The folder names and the file name of a path, each checked against the rule for its place.
func _check_name(path: String) -> void:
	var relative := path.trim_prefix("res://")
	var parts := relative.split("/")
	var in_source := path.begins_with(SOURCE + "/")
	if VENDOR_FILES.has(path.trim_suffix(".import")):
		return
	# A README is named for what it is, wherever it sits.
	if parts[-1] == "README.md":
		return
	if parts.size() == 1 and (ROOT_EXTENSIONS.has(parts[0].get_extension()) or parts[0].begins_with(".")):
		return
	# A .uid or .import file is named after the file it belongs to.
	var file_name := parts[-1]
	for suffix in [".uid", ".import"]:
		file_name = file_name.trim_suffix(suffix)
	var stem := file_name.get_basename()
	if parts.size() > 1:
		for i in parts.size() - 1:
			if in_source and i == 0:
				continue
			if not _matches(parts[i], PASCAL_CASE if in_source else SNAKE_CASE):
				_problems.append("%s: the folder %s should be %s." % [path, parts[i], "PascalCase" if in_source else "snake_case"])
				return
	if not _matches(stem, PASCAL_CASE if in_source else SNAKE_CASE):
		_problems.append("%s: the file %s should be %s." % [path, stem, "PascalCase" if in_source else "snake_case"])


func _matches(text: String, pattern: String) -> bool:
	return RegEx.create_from_string(pattern).search(text) != null
'''

README = r'''# TopDownTemplate

A stylized top-down 3D game template for Godot 4.8 (.NET): a hand-painted meadow with grass, trees, and water, a day and night cycle, a character, a camera rig, and a pause panel. Copy it, rename it, and start a game.

## Requirements

- Godot 4.8 (.NET build)
- .NET SDK 10

## Folders

| Folder | What it holds |
|---|---|
| `art/` | The art library: models, materials, shaders, and textures. It holds no scripts and never refers to anything outside itself. See `art/README.md`. |
| `art_source/` | The source files the art is made from, such as Blender and Krita files. |
| `levels/` | Scenes you play: the hand-built meadow and the generated level. |
| `src/` | All C# code. A folder is a namespace. |
| `tools/` | Editor scripts for the project itself, such as the audit. |
| `ui/` | The theme and the interface scenes. |
| `world/` | The scenes a level is made from: the camera rig, the environment, the player, the ground data, and the generator. |

## Conventions

- Files and folders outside `src/` are `snake_case`. Inside `src/`, folders and C# files are `PascalCase`, and a file is named after the class in it.
- Nodes are `PascalCase`. Input actions and shader globals are `snake_case`.
- C# uses file-scoped namespaces, nullable reference types, and one namespace root, the project's name. Warnings are errors.
- Run `tools/audit_project.gd` from the Script editor (File > Run) before you commit. It checks the art boundary and the names above.

## Layers

The first layer is `World`, so a static prop dropped into a level needs no setting changed. A body's layer says what it is, and its mask says what it collides with.

| Layer | Physics | Render |
|---|---|---|
| 1 | World | World |
| 2 | Terrain | Terrain |
| 3 | Hazard | Foliage |
| 4 | Interactable | Water |
| 5 | Player | Characters |
| 6 | Enemy | Effects |
| 7 | Npc | |
| 8 | Destructible | |
| 9 | Hurtbox | |
| 10 | Projectile | |
| 11 | Pickup | |
| 12 | Sensor | |

## Window

The base size is 1920 by 1080 with the `canvas_items` stretch mode and the `expand` aspect, and the camera keeps its height. Any window shape is filled with no bars, and a wider one shows more of the world.
'''

ART_README = r'''# Art library

Everything the game draws: models, materials, shaders, and textures. The folder is self-contained, so it can be copied into another game or kept in a repository of its own.

## Rules

- It holds no scripts. Optional scripts that use the art live in `src/` and are attached in `world/` or `levels/`.
- It never refers to `world/`, `levels/`, `ui/`, or `src/`. `tools/audit_project.gd` checks this.
- It keeps the name `art` at the project's root, because its shaders include each other by `res://art/...` paths.
- Its source files are in `art_source/`.

## What it needs from the project

The shaders read these shader globals, set in Project Settings under Globals:

| Global | Type | Used for |
|---|---|---|
| `wind_direction` | `vec2` | The way the wind blows. |
| `wind_strength` | `float` | How hard it blows. |
| `push_point` | `vec4` | Where grass bends away from the player. |
| `rim_color` | `vec4` color | The color of the soft rim light. |
| `rim_strength` | `float` | How strong the rim light is. |
| `cloud_texture` | `sampler2D` | The noise the cloud shadows are cut from. |
| `cloud_scale` | `float` | The size of a cloud shadow in meters. |
| `cloud_strength` | `float` | How dark a cloud shadow is. |

`character/character.tscn` has an `AnimationTree` with a blend space on `parameters/blend_position`: set it to the speed of the body and the character walks and runs. The tree is off in the saved scene, so a script turns it on.
'''
