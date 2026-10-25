# Lesson 13: the grass detail, drawn by a C# tool script. Four pieces: an empty gray picture, one blade, a field of
# blades, and the finished drawing with tone and a faint shadow. Each piece is built and run from the Script editor.
# Then the picture is imported with the settings a repeating 3D texture needs.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import (write, eval_, save_code, build, make_folder, new_script, run_tool_script, click_tab, click_file,
                   DUMP_IMPORT, import_set, show_import_row, REIMPORT)

PIECES = ['using System;\nusing Godot;\n\nnamespace TopDownTemplate.Tools;\n\n// Draws the grass detail, a gray image of overlapping blades that the ground shader tints. Run it from the Script editor with File > Run.\n[Tool]\npublic partial class GrassDetail : EditorScript\n{\n\tprivate const int Size = 1024;\n\tprivate const string Path = "res://art/ground/grass_detail.png";\n\n\tprivate readonly float[] _values = new float[Size * Size];\n\n\tpublic override void _Run()\n\t{\n\t\t// The gaps between the blades start darker than the blades.\n\t\tArray.Fill(_values, 0.72f);\n\t\tSave();\n\t}\n\n\tprivate void Save()\n\t{\n\t\tvar bytes = new byte[Size * Size];\n\t\tfor (var i = 0; i < bytes.Length; i++)\n\t\t{\n\t\t\tbytes[i] = (byte)(Math.Clamp(_values[i], 0f, 1f) * 255f);\n\t\t}\n\n\t\tvar image = Image.CreateFromData(Size, Size, false, Image.Format.L8, bytes);\n\t\timage.SavePng(ProjectSettings.GlobalizePath(Path));\n\t\tEditorInterface.Singleton.GetResourceFilesystem().Scan();\n\t\tGD.Print($"Saved {Path}");\n\t}\n}\n', 'using System;\nusing Godot;\n\nnamespace TopDownTemplate.Tools;\n\n// Draws the grass detail, a gray image of overlapping blades that the ground shader tints. Run it from the Script editor with File > Run.\n[Tool]\npublic partial class GrassDetail : EditorScript\n{\n\tprivate const int Size = 1024;\n\tprivate const string Path = "res://art/ground/grass_detail.png";\n\n\tprivate readonly float[] _values = new float[Size * Size];\n\n\tpublic override void _Run()\n\t{\n\t\t// The gaps between the blades start darker than the blades.\n\t\tArray.Fill(_values, 0.72f);\n\t\tDrawBlade(Size / 2f, Size / 2f, -MathF.PI / 2f, 150f, 40f, 0.15f, 0.9f);\n\t\tSave();\n\t}\n\n\tprivate void Save()\n\t{\n\t\tvar bytes = new byte[Size * Size];\n\t\tfor (var i = 0; i < bytes.Length; i++)\n\t\t{\n\t\t\tbytes[i] = (byte)(Math.Clamp(_values[i], 0f, 1f) * 255f);\n\t\t}\n\n\t\tvar image = Image.CreateFromData(Size, Size, false, Image.Format.L8, bytes);\n\t\timage.SavePng(ProjectSettings.GlobalizePath(Path));\n\t\tEditorInterface.Singleton.GetResourceFilesystem().Scan();\n\t\tGD.Print($"Saved {Path}");\n\t}\n\n\tprivate static float Range(Random random, float low, float high)\n\t{\n\t\treturn low + random.NextSingle() * (high - low);\n\t}\n\n\tprivate static float Smooth(float low, float high, float x)\n\t{\n\t\tvar t = Math.Clamp((x - low) / (high - low), 0f, 1f);\n\t\treturn t * t * (3f - 2f * t);\n\t}\n\n\t// How much of a pixel a blade covers, 0 to 1, and how far along the blade the pixel is. A blade is curved, widest\n\t// near its root, and tapers to a point.\n\tprivate static (float Cover, float Tip) Cover(float dx, float dy, float heading, float length, float width, float bend)\n\t{\n\t\tvar along = dx * MathF.Cos(heading) + dy * MathF.Sin(heading);\n\t\tvar across = dy * MathF.Cos(heading) - dx * MathF.Sin(heading) - bend * along * along / length;\n\t\tvar tip = along / length;\n\t\tif (tip is < -0.1f or >= 1f)\n\t\t{\n\t\t\treturn (0f, tip);\n\t\t}\n\n\t\tvar half = width / 2f * MathF.Pow(Math.Clamp(1f - tip, 0f, 1f), 0.8f) * Smooth(-0.1f, 0.12f, tip);\n\t\tvar edge = 1f - MathF.Abs(across) / MathF.Max(half, 1e-6f);\n\t\treturn (Smooth(0f, 0.1f, edge), tip);\n\t}\n\n\tprivate void DrawBlade(float rootX, float rootY, float heading, float length, float width, float bend, float shade)\n\t{\n\t\tvar reach = (int)length + 6;\n\t\tfor (var y = (int)rootY - reach; y <= (int)rootY + reach; y++)\n\t\t{\n\t\t\tfor (var x = (int)rootX - reach; x <= (int)rootX + reach; x++)\n\t\t\t{\n\t\t\t\tvar (cover, tip) = Cover(x + 0.5f - rootX, y + 0.5f - rootY, heading, length, width, bend);\n\t\t\t\tif (cover <= 0f)\n\t\t\t\t{\n\t\t\t\t\tcontinue;\n\t\t\t\t}\n\n\t\t\t\t// The picture wraps at its edges, so it tiles.\n\t\t\t\tvar index = (((y % Size) + Size) % Size) * Size + ((x % Size) + Size) % Size;\n\t\t\t\tvar color = shade * (0.97f + 0.06f * Math.Clamp(tip, 0f, 1f));\n\t\t\t\t_values[index] = _values[index] * (1f - cover) + color * cover;\n\t\t\t}\n\t\t}\n\t}\n}\n', 'using System;\nusing Godot;\n\nnamespace TopDownTemplate.Tools;\n\n// Draws the grass detail, a gray image of overlapping blades that the ground shader tints. Run it from the Script editor with File > Run.\n[Tool]\npublic partial class GrassDetail : EditorScript\n{\n\tprivate const int Size = 1024;\n\tprivate const string Path = "res://art/ground/grass_detail.png";\n\n\tprivate readonly float[] _values = new float[Size * Size];\n\n\tpublic override void _Run()\n\t{\n\t\tvar random = new Random(404);\n\t\t// The gaps between the blades start darker than the blades.\n\t\tArray.Fill(_values, 0.72f);\n\n\t\tfor (var cluster = 0; cluster < 150; cluster++)\n\t\t{\n\t\t\tvar rootX = random.NextSingle() * Size;\n\t\t\tvar rootY = random.NextSingle() * Size;\n\t\t\t// Blades point up the screen, fanned out.\n\t\t\tvar heading = -MathF.PI / 2f + Range(random, -0.9f, 0.9f);\n\t\t\tvar blades = random.Next(4, 7);\n\t\t\tfor (var order = 0; order < blades; order++)\n\t\t\t{\n\t\t\t\tDrawBlade(\n\t\t\t\t\trootX + Range(random, -13f, 13f),\n\t\t\t\t\trootY + Range(random, -13f, 13f),\n\t\t\t\t\theading + Range(random, -0.45f, 0.45f),\n\t\t\t\t\tRange(random, 114f, 176f),\n\t\t\t\t\tRange(random, 31f, 44f),\n\t\t\t\t\tRange(random, -0.25f, 0.25f),\n\t\t\t\t\t0.88f);\n\t\t\t}\n\t\t}\n\n\t\tSave();\n\t}\n\n\tprivate void Save()\n\t{\n\t\tvar bytes = new byte[Size * Size];\n\t\tfor (var i = 0; i < bytes.Length; i++)\n\t\t{\n\t\t\tbytes[i] = (byte)(Math.Clamp(_values[i], 0f, 1f) * 255f);\n\t\t}\n\n\t\tvar image = Image.CreateFromData(Size, Size, false, Image.Format.L8, bytes);\n\t\timage.SavePng(ProjectSettings.GlobalizePath(Path));\n\t\tEditorInterface.Singleton.GetResourceFilesystem().Scan();\n\t\tGD.Print($"Saved {Path}");\n\t}\n\n\tprivate static float Range(Random random, float low, float high)\n\t{\n\t\treturn low + random.NextSingle() * (high - low);\n\t}\n\n\tprivate static float Smooth(float low, float high, float x)\n\t{\n\t\tvar t = Math.Clamp((x - low) / (high - low), 0f, 1f);\n\t\treturn t * t * (3f - 2f * t);\n\t}\n\n\t// How much of a pixel a blade covers, 0 to 1, and how far along the blade the pixel is. A blade is curved, widest\n\t// near its root, and tapers to a point.\n\tprivate static (float Cover, float Tip) Cover(float dx, float dy, float heading, float length, float width, float bend)\n\t{\n\t\tvar along = dx * MathF.Cos(heading) + dy * MathF.Sin(heading);\n\t\tvar across = dy * MathF.Cos(heading) - dx * MathF.Sin(heading) - bend * along * along / length;\n\t\tvar tip = along / length;\n\t\tif (tip is < -0.1f or >= 1f)\n\t\t{\n\t\t\treturn (0f, tip);\n\t\t}\n\n\t\tvar half = width / 2f * MathF.Pow(Math.Clamp(1f - tip, 0f, 1f), 0.8f) * Smooth(-0.1f, 0.12f, tip);\n\t\tvar edge = 1f - MathF.Abs(across) / MathF.Max(half, 1e-6f);\n\t\treturn (Smooth(0f, 0.1f, edge), tip);\n\t}\n\n\tprivate void DrawBlade(float rootX, float rootY, float heading, float length, float width, float bend, float shade)\n\t{\n\t\tvar reach = (int)length + 6;\n\t\tfor (var y = (int)rootY - reach; y <= (int)rootY + reach; y++)\n\t\t{\n\t\t\tfor (var x = (int)rootX - reach; x <= (int)rootX + reach; x++)\n\t\t\t{\n\t\t\t\tvar (cover, tip) = Cover(x + 0.5f - rootX, y + 0.5f - rootY, heading, length, width, bend);\n\t\t\t\tif (cover <= 0f)\n\t\t\t\t{\n\t\t\t\t\tcontinue;\n\t\t\t\t}\n\n\t\t\t\t// The picture wraps at its edges, so it tiles.\n\t\t\t\tvar index = (((y % Size) + Size) % Size) * Size + ((x % Size) + Size) % Size;\n\t\t\t\tvar color = shade * (0.97f + 0.06f * Math.Clamp(tip, 0f, 1f));\n\t\t\t\t_values[index] = _values[index] * (1f - cover) + color * cover;\n\t\t\t}\n\t\t}\n\t}\n}\n', 'using System;\nusing Godot;\n\nnamespace TopDownTemplate.Tools;\n\n// Draws the grass detail, a gray image of overlapping blades that the ground shader tints. Run it from the Script editor with File > Run.\n[Tool]\npublic partial class GrassDetail : EditorScript\n{\n\tprivate const int Size = 1024;\n\tprivate const string Path = "res://art/ground/grass_detail.png";\n\n\tprivate readonly float[] _values = new float[Size * Size];\n\n\tpublic override void _Run()\n\t{\n\t\tvar random = new Random(404);\n\t\t// The gaps between the blades start darker than the blades.\n\t\tArray.Fill(_values, 0.72f);\n\n\t\tfor (var cluster = 0; cluster < 150; cluster++)\n\t\t{\n\t\t\tvar rootX = random.NextSingle() * Size;\n\t\t\tvar rootY = random.NextSingle() * Size;\n\t\t\t// Blades point up the screen, fanned out.\n\t\t\tvar heading = -MathF.PI / 2f + Range(random, -0.9f, 0.9f);\n\t\t\tvar tone = Range(random, -0.04f, 0.04f);\n\t\t\tvar blades = random.Next(4, 7);\n\t\t\tfor (var order = 0; order < blades; order++)\n\t\t\t{\n\t\t\t\t// Drawn back to front: each blade a little lighter than the one behind it.\n\t\t\t\tvar shade = 0.84f + 2f * tone + 0.05f * order / 5f;\n\t\t\t\tDrawBlade(\n\t\t\t\t\trootX + Range(random, -13f, 13f),\n\t\t\t\t\trootY + Range(random, -13f, 13f),\n\t\t\t\t\theading + Range(random, -0.45f, 0.45f),\n\t\t\t\t\tRange(random, 114f, 176f),\n\t\t\t\t\tRange(random, 31f, 44f),\n\t\t\t\t\tRange(random, -0.25f, 0.25f),\n\t\t\t\t\tshade);\n\t\t\t}\n\t\t}\n\n\t\tSave();\n\t}\n\n\tprivate void Save()\n\t{\n\t\tvar bytes = new byte[Size * Size];\n\t\tfor (var i = 0; i < bytes.Length; i++)\n\t\t{\n\t\t\tbytes[i] = (byte)(Math.Clamp(_values[i], 0f, 1f) * 255f);\n\t\t}\n\n\t\tvar image = Image.CreateFromData(Size, Size, false, Image.Format.L8, bytes);\n\t\timage.SavePng(ProjectSettings.GlobalizePath(Path));\n\t\tEditorInterface.Singleton.GetResourceFilesystem().Scan();\n\t\tGD.Print($"Saved {Path}");\n\t}\n\n\tprivate static float Range(Random random, float low, float high)\n\t{\n\t\treturn low + random.NextSingle() * (high - low);\n\t}\n\n\tprivate static float Smooth(float low, float high, float x)\n\t{\n\t\tvar t = Math.Clamp((x - low) / (high - low), 0f, 1f);\n\t\treturn t * t * (3f - 2f * t);\n\t}\n\n\t// How much of a pixel a blade covers, 0 to 1, and how far along the blade the pixel is. A blade is curved, widest\n\t// near its root, and tapers to a point.\n\tprivate static (float Cover, float Tip) Cover(float dx, float dy, float heading, float length, float width, float bend)\n\t{\n\t\tvar along = dx * MathF.Cos(heading) + dy * MathF.Sin(heading);\n\t\tvar across = dy * MathF.Cos(heading) - dx * MathF.Sin(heading) - bend * along * along / length;\n\t\tvar tip = along / length;\n\t\tif (tip is < -0.1f or >= 1f)\n\t\t{\n\t\t\treturn (0f, tip);\n\t\t}\n\n\t\tvar half = width / 2f * MathF.Pow(Math.Clamp(1f - tip, 0f, 1f), 0.8f) * Smooth(-0.1f, 0.12f, tip);\n\t\tvar edge = 1f - MathF.Abs(across) / MathF.Max(half, 1e-6f);\n\t\treturn (Smooth(0f, 0.1f, edge), tip);\n\t}\n\n\tprivate void DrawBlade(float rootX, float rootY, float heading, float length, float width, float bend, float shade)\n\t{\n\t\tvar reach = (int)length + 6;\n\t\tfor (var pass = 0; pass < 2; pass++)\n\t\t{\n\t\t\t// Pass 0 darkens the gaps a little down and right of the blade, a faint shadow. Pass 1 paints the blade.\n\t\t\tvar offsetX = pass == 0 ? 4f : 0f;\n\t\t\tvar offsetY = pass == 0 ? 9f : 0f;\n\t\t\tfor (var y = (int)rootY - reach; y <= (int)rootY + reach; y++)\n\t\t\t{\n\t\t\t\tfor (var x = (int)rootX - reach; x <= (int)rootX + reach; x++)\n\t\t\t\t{\n\t\t\t\t\tvar (cover, tip) = Cover(x + 0.5f - rootX - offsetX, y + 0.5f - rootY - offsetY, heading, length, width, bend);\n\t\t\t\t\tif (cover <= 0f)\n\t\t\t\t\t{\n\t\t\t\t\t\tcontinue;\n\t\t\t\t\t}\n\n\t\t\t\t\t// The picture wraps at its edges, so it tiles.\n\t\t\t\t\tvar index = (((y % Size) + Size) % Size) * Size + ((x % Size) + Size) % Size;\n\t\t\t\t\tif (pass == 0)\n\t\t\t\t\t{\n\t\t\t\t\t\t_values[index] *= 1f - 0.07f * cover;\n\t\t\t\t\t}\n\t\t\t\t\telse\n\t\t\t\t\t{\n\t\t\t\t\t\tvar color = shade * (0.97f + 0.06f * Math.Clamp(tip, 0f, 1f));\n\t\t\t\t\t\t_values[index] = _values[index] * (1f - cover) + color * cover;\n\t\t\t\t\t}\n\t\t\t\t}\n\t\t\t}\n\t\t}\n\t}\n}\n']
SCRIPT = 'res://src/Tools/GrassDetail.cs'
PICTURE = 'res://art/ground/grass_detail.png'


def keep_picture(name):
    # Reads the picture back (mean and spread of its gray) and keeps a copy for the figures.
    return eval_(f'''
var image := Image.load_from_file(ProjectSettings.globalize_path("{PICTURE}"))
var total := 0.0
var spread := 0.0
var count := image.get_width() * image.get_height()
for y in image.get_height():
	for x in image.get_width():
		total += image.get_pixel(x, y).r
var mean := total / count
for y in image.get_height():
	for x in image.get_width():
		spread += pow(image.get_pixel(x, y).r - mean, 2)
print("[probe] {name} size ", image.get_size(), " mean ", snappedf(mean, 0.001), " spread ", snappedf(sqrt(spread / count), 0.001))
DirAccess.copy_absolute(ProjectSettings.globalize_path("{PICTURE}"), OS.get_environment("CAPTURE_OUT").path_join("l13_{name}.png"))
''')


steps = [
    {'op': 'sleep', 'seconds': 3},
    *make_folder('src', 'Tools'),
    *make_folder('art', 'ground'),
    {'op': 'fs', 'path': 'res://src/Tools'},
    *new_script(SCRIPT, 'EditorScript', 'l13_new_script'),
]
for number, piece in enumerate(PIECES, 1):
    steps += [
        save_code(SCRIPT, piece),
        *build(),
        *run_tool_script(SCRIPT),
        keep_picture(f'piece{number}'),
    ]
steps += [
    {'op': 'main_screen', 'name': '3D'},
    {'op': 'fs', 'path': PICTURE},
    *click_file('grass_detail.png'),
    click_tab('Import'),
    {'op': 'wait', 'frames': 30},
    DUMP_IMPORT,
    {'op': 'capture', 'name': 'l13_import_before'},
    # VRAM Compressed: the graphics card keeps it compressed, a quarter of the memory or less.
    import_set('compress/mode', 2),
    {'op': 'wait', 'frames': 20},
    show_import_row('mipmaps/generate'),
    import_set('mipmaps/generate', 'true'),
    {'op': 'wait', 'frames': 20},
    {'op': 'capture', 'name': 'l13_import_set'},
    REIMPORT,
    {'op': 'sleep', 'seconds': 3},
    eval_('''
var cfg := ConfigFile.new()
cfg.load("res://art/ground/grass_detail.png.import")
var texture: Texture2D = load("res://art/ground/grass_detail.png")
print("[probe] grass import compress ", cfg.get_value("params", "compress/mode"), " mipmaps ", cfg.get_value("params", "mipmaps/generate"), " size ", texture.get_size(), " format ", texture.get_image().get_format(), " mipmaps ", texture.get_image().has_mipmaps())
'''),
    {'op': 'wait', 'frames': 30},
    {'op': 'capture', 'name': 'l13_import_after'},
    {'op': 'quit'},
]
write(sys.argv[2], steps)
