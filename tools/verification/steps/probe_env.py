# Probe: Environment and DirectionalLight3D property names and defaults in this Godot build.
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_

steps = [
    {'op': 'sleep', 'seconds': 3},
    eval_('''
for cls in ["Environment", "Sky", "DirectionalLight3D"]:
	var out := []
	for info in ClassDB.class_get_property_list(cls, true):
		if info.usage & PROPERTY_USAGE_EDITOR:
			out.append("%s=%s" % [info.name, ClassDB.class_get_property_default_value(cls, info.name)])
	print("[probe] ", cls, " ", "\\n".join(out))
print("[probe] version ", Engine.get_version_info().string)
'''),
]
write(sys.argv[2], steps)
