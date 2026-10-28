# The code and text of lesson 60, shared by the step scripts and the page's checkpoint.

RENAME = r'''extends SceneTree

# Gives a copy of the template its own name. Close Godot, then run it once from the copy's folder:
#   godot --headless --path . --script res://tools/rename_project.gd -- "Studio Name" GameName
# Add --dry-run to list what would change without changing anything. It renames the project, the C# assembly and
# namespace root, the solution and project files, the user data folder, and the export bundle identifier, clears the
# build files that carry the old name, and deletes itself.

const USAGE := "Usage: godot --headless --path . --script res://tools/rename_project.gd -- \"Studio Name\" GameName [--dry-run]"
# The files that carry the project's name, and the folders that never do.
const TEXT_EXTENSIONS := ["cs", "csproj", "sln", "md", "cfg", "godot"]
const SKIPPED := ["res://.godot", "res://.git", "res://.idea", "res://.vscode", "res://builds", "res://art", "res://art_source"]
const GAME_NAME := "^[A-Z][A-Za-z0-9]*$"
const STUDIO_NAME := "^[A-Za-z0-9][A-Za-z0-9 _-]*$"

var _dry_run := false


func _init() -> void:
	var arguments := Array(OS.get_cmdline_user_args())
	_dry_run = arguments.has("--dry-run")
	arguments = arguments.filter(func(argument: String) -> bool: return not argument.begins_with("--"))
	if arguments.size() != 2:
		_fail(USAGE)
		return
	var studio: String = arguments[0]
	var game: String = arguments[1]
	if RegEx.create_from_string(GAME_NAME).search(game) == null:
		_fail("The game name must be letters and digits starting with a capital letter, because it becomes a C# namespace: %s" % game)
		return
	if RegEx.create_from_string(STUDIO_NAME).search(studio) == null:
		_fail("The studio name must be letters, digits, spaces, hyphens, and underscores: %s" % studio)
		return
	var old_name := str(ProjectSettings.get_setting("application/config/name"))
	if old_name == game:
		_fail("The project is already named %s." % game)
		return
	for file in ["%s.csproj" % old_name, "%s.sln" % old_name]:
		if not FileAccess.file_exists("res://" + file):
			_fail("This is not a copy of the template: res://%s is missing." % file)
			return

	var identifier := "com.%s.%s" % [_lowercase_letters(studio), game.to_lower()]
	for path in _files("res://"):
		if TEXT_EXTENSIONS.has(path.get_extension()):
			_edit(path, old_name, game, studio, identifier)
	for extension in ["csproj", "sln"]:
		_rename("res://%s.%s" % [old_name, extension], "res://%s.%s" % [game, extension])
	for folder in ["res://.godot/mono", "res://bin", "res://obj"]:
		_remove_folder(folder)
	if not _dry_run:
		DirAccess.remove_absolute("res://tools/rename_project.gd")
		DirAccess.remove_absolute("res://tools/rename_project.gd.uid")
	print("%s %s as %s by %s. Open the project in Godot and build it." % ["Would rename" if _dry_run else "Renamed", old_name, game, studio])
	quit()


func _fail(message: String) -> void:
	printerr(message)
	quit(1)


# Every file under a folder, skipping the folders that never carry the name.
func _files(folder: String) -> Array[String]:
	var found: Array[String] = []
	for entry in DirAccess.get_files_at(folder):
		found.append(folder.path_join(entry))
	for entry in DirAccess.get_directories_at(folder):
		var path := folder.path_join(entry)
		if not SKIPPED.has(path):
			found.append_array(_files(path))
	return found


# Replaces the old name, as a whole word, in one file, and sets the lines that are not the name alone.
func _edit(path: String, old_name: String, game: String, studio: String, identifier: String) -> void:
	var text := FileAccess.get_file_as_string(path)
	var edited := RegEx.create_from_string("\\b%s\\b" % old_name).sub(text, game, true)
	if path == "res://project.godot":
		edited = RegEx.create_from_string("config/custom_user_dir_name=\"[^\"]*\"").sub(edited, "config/custom_user_dir_name=\"%s/%s\"" % [studio, game])
	elif path == "res://export_presets.cfg":
		edited = RegEx.create_from_string("application/bundle_identifier=\"[^\"]*\"").sub(edited, "application/bundle_identifier=\"%s\"" % identifier)
	elif path == "res://README.md":
		# The instructions for starting a game have done their job.
		edited = RegEx.create_from_string("(?s)## Start a new game.*?(?=\\n## |\\z)").sub(edited, "")
	if edited == text:
		return
	print("%s %s" % ["Would edit" if _dry_run else "Edited", path])
	if not _dry_run:
		var file := FileAccess.open(path, FileAccess.WRITE)
		file.store_string(edited)
		file.close()


func _rename(from: String, to: String) -> void:
	print("%s %s to %s" % ["Would rename" if _dry_run else "Renamed", from, to])
	if not _dry_run:
		DirAccess.rename_absolute(from, to)


# Build files hold the old assembly name, and Godot makes them again.
func _remove_folder(folder: String) -> void:
	if not DirAccess.dir_exists_absolute(folder):
		return
	print("%s %s" % ["Would remove" if _dry_run else "Removed", folder])
	if not _dry_run:
		_delete_tree(folder)


func _delete_tree(folder: String) -> void:
	for file in DirAccess.get_files_at(folder):
		DirAccess.remove_absolute(folder.path_join(file))
	for sub in DirAccess.get_directories_at(folder):
		_delete_tree(folder.path_join(sub))
	DirAccess.remove_absolute(folder)


# A studio name as it goes into a bundle identifier: lowercase letters and digits only.
func _lowercase_letters(text: String) -> String:
	return RegEx.create_from_string("[^a-z0-9]").sub(text.to_lower(), "", true)
'''

README_SECTION = r'''## Start a new game

1. Close Godot, copy the whole project folder, and delete `.godot`, `builds`, and `.git` from the copy.
2. In the copy, run the rename script once with the Godot .NET executable. Add `--dry-run` first to see what it would change:

   ```
   godot --headless --path . --script res://tools/rename_project.gd -- "Studio Name" GameName
   ```

3. Open the project in Godot and click Build Project.

'''
