@tool
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
