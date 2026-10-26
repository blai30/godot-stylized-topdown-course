# Prototype: FactoryGame's grass clumps and shader scattered over the meadow at runtime, to judge the look in the real renderer.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, game_steps, play

CLOCK = 'Meadow/WorldEnvironment/Day'

SCATTER = '''
var meadow := tree.root.get_node("Meadow")
var gridmap: GridMap = meadow.get_node("GroundTiles")
var ground: ShaderMaterial = gridmap.mesh_library.get_item_mesh(0).surface_get_material(0)
var material := ShaderMaterial.new()
material.shader = load("res://art/shaders/grass.gdshader")
material.set_shader_parameter("ground_texture", ground.get_shader_parameter("albedo_texture"))
material.set_shader_parameter("ground_tint", ground.get_shader_parameter("albedo_tint"))
material.set_shader_parameter("field_noise", ground.get_shader_parameter("edge_noise"))
var meshes := []
for variant in ["a", "b", "c"]:
	var scene: Node = load("res://art/nature/grass_proto/grass_clump_%s.glb" % variant).instantiate()
	meshes.append(scene.find_children("*", "MeshInstance3D", true, false)[0].mesh)
var transforms := [[], [], []]
var rng := RandomNumberGenerator.new()
rng.seed = 7
for sx in range(-10, 10):
	for sz in range(-10, 10):
		for half in range(2):
			var x := sx + 0.25 + 0.5 * half + rng.randf_range(-0.2, 0.2)
			var z := sz + rng.randf()
			var item := gridmap.get_cell_item(gridmap.local_to_map(Vector3(x, 0.0, z)))
			var density := 1.0 if item == 0 else (0.1 if item == 2 else 0.0)
			if rng.randf() >= density:
				continue
			var basis := Basis(Vector3.UP, rng.randf() * TAU).scaled(Vector3.ONE * rng.randf_range(0.9, 1.1))
			transforms[rng.randi() % 3].append([Transform3D(basis, Vector3(x, 0.0, z)), rng.randf()])
var total := 0
for i in 3:
	var multimesh := MultiMesh.new()
	multimesh.transform_format = MultiMesh.TRANSFORM_3D
	multimesh.use_custom_data = true
	multimesh.mesh = meshes[i]
	multimesh.instance_count = transforms[i].size()
	for j in transforms[i].size():
		multimesh.set_instance_transform(j, transforms[i][j][0])
		multimesh.set_instance_custom_data(j, Color(transforms[i][j][1], 0.0, 0.0, 0.0))
	var instance := MultiMeshInstance3D.new()
	instance.multimesh = multimesh
	instance.material_override = material
	instance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	meadow.add_child(instance)
	total += transforms[i].size()
var flower_material := ShaderMaterial.new()
flower_material.shader = load("res://art/shaders/flower.gdshader")
var flower_meshes := []
for flower in ["daisy", "cup"]:
	var scene: Node = load("res://art/nature/grass_proto/flower_%s.glb" % flower).instantiate()
	flower_meshes.append(scene.find_children("*", "MeshInstance3D", true, false)[0].mesh)
var colors := [Color("#FFD23F"), Color("#FF7EB6"), Color("#FFFFFF"), Color("#8FA9FF")]
var flowers := [[], []]
rng.seed = 11
for sx in range(-10, 10):
	for sz in range(-10, 10):
		var x := sx + rng.randf()
		var z := sz + rng.randf()
		var item := gridmap.get_cell_item(gridmap.local_to_map(Vector3(x, 0.0, z)))
		if item != 0 or rng.randf() >= 0.3:
			continue
		flowers[rng.randi() % 2].append([Transform3D(Basis(Vector3.UP, rng.randf() * TAU), Vector3(x, 0.0, z)), rng.randf(), colors[rng.randi() % 4]])
for i in 2:
	var multimesh := MultiMesh.new()
	multimesh.transform_format = MultiMesh.TRANSFORM_3D
	multimesh.use_custom_data = true
	multimesh.use_colors = true
	multimesh.mesh = flower_meshes[i]
	multimesh.instance_count = flowers[i].size()
	for j in flowers[i].size():
		multimesh.set_instance_transform(j, flowers[i][j][0])
		multimesh.set_instance_custom_data(j, Color(flowers[i][j][1], 0.0, 0.0, 0.0))
		multimesh.set_instance_color(j, flowers[i][j][2])
	var instance := MultiMeshInstance3D.new()
	instance.multimesh = multimesh
	instance.material_override = flower_material
	instance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	meadow.add_child(instance)
	total += flowers[i].size()
print("[proto] clumps and flowers ", total)
'''


def hour(time, name, wheel=0):
    steps = [{'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", {time})'}]
    if wheel:
        steps.append({'op': 'wheel', 'steps': wheel})
    steps += [{'op': 'wait', 'frames': 50}, {'op': 'capture', 'name': f'protog_{name}', 'frames': 10}]
    if wheel:
        steps.append({'op': 'wheel', 'steps': -wheel})
    return steps


out_dir = os.path.dirname(sys.argv[2])
game = game_steps(os.path.join(out_dir, 'game-protog.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    eval_(SCATTER),
    {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)'},
    *hour(0.5, 'noon'), *hour(0.5, 'noon_close', 5), *hour(0.5, 'noon_closer', 9), *hour(0.5, 'noon_max', 14), *hour(0.0, 'night_close', 5),
    {'op': 'quit'}])
steps = [{'op': 'sleep', 'seconds': 15}, *play(game, 40)]
write(sys.argv[2], steps)
