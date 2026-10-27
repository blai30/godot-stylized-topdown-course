# Prototype: the ported water shader on a painted pond in the meadow, to judge the look in the real renderer.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, game_steps, play

CLOCK = 'Meadow/WorldEnvironment/Day'

POND = '''
var meadow := tree.root.get_node("Meadow")
var gridmap: GridMap = meadow.get_node("GroundTiles")
var ground: ShaderMaterial = gridmap.mesh_library.get_item_mesh(0).surface_get_material(0)

var noise := FastNoiseLite.new()
noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
noise.frequency = 0.02
var waves := NoiseTexture2D.new()
waves.noise = noise
waves.seamless = true
waves.as_normal_map = true
waves.bump_strength = 6.0
waves.width = 256
waves.height = 256
await waves.changed

var bed_material := ShaderMaterial.new()
bed_material.shader = load("res://art/shaders/lake_bed.gdshader")
bed_material.set_shader_parameter("albedo_texture", load("res://art/ground/dirt_albedo.png"))
bed_material.set_shader_parameter("edge_noise", ground.get_shader_parameter("edge_noise"))
bed_material.set_shader_parameter("wave_normals", waves)
var water_material := ShaderMaterial.new()
water_material.shader = load("res://art/shaders/water.gdshader")
water_material.set_shader_parameter("wave_normals", waves)

var plane := PlaneMesh.new()
plane.size = Vector2(0.5, 0.5)
var mesh := ArrayMesh.new()
for layer in [[-0.75, bed_material]]:
	var arrays := plane.get_mesh_arrays()
	var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
	for i in vertices.size():
		vertices[i].y = layer[0]
	arrays[Mesh.ARRAY_VERTEX] = vertices
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	mesh.surface_set_material(mesh.get_surface_count() - 1, layer[1])
var water_surface := MeshInstance3D.new()
var water_plane := PlaneMesh.new()
water_plane.size = Vector2(19.6, 19.6)
water_surface.mesh = water_plane
water_surface.material_override = water_material
water_surface.position = Vector3(0.0, -0.35, 0.0)
water_surface.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
meadow.add_child(water_surface)
gridmap.mesh_library.create_item(3)
gridmap.mesh_library.set_item_mesh(3, mesh)

var center := Vector2(POND_X, POND_Z)
for cx in range(-60, 60):
	for cz in range(-60, 60):
		var p := Vector2(cx, cz) * 0.5
		var d := (p - center) / Vector2(4.2, 3.0)
		if d.length() < 1.0 + 0.15 * sin(p.x * 1.7) + 0.1 * cos(p.y * 2.3):
			gridmap.set_cell_item(Vector3i(cx, 0, cz), 3)


if STAGE_ON:
	for cell in gridmap.get_used_cells():
		if gridmap.get_cell_item(cell) == 3:
			gridmap.set_cell_item(cell, 0)
	# A lake with cut corners, a one-cell channel, a diagonal pair, a lone cell, and an island.
	for x in range(-12, -2):
		for z in range(-10, -3):
			if (x in [-12, -3] and z in [-10, -4]) or (x == -11 and z == -10):
				continue
			gridmap.set_cell_item(Vector3i(x, 0, z), 3)
	for x in range(-2, 12):
		gridmap.set_cell_item(Vector3i(x, 0, -7), 3)
	for cell in [Vector3i(2, 0, 0), Vector3i(3, 0, 1), Vector3i(8, 0, 0), Vector3i(9, 0, 0), Vector3i(9, 0, 1), Vector3i(-6, 0, 1)]:
		gridmap.set_cell_item(cell, 3)
	for cell in [Vector3i(-8, 0, -7), Vector3i(-7, 0, -7), Vector3i(-8, 0, -6)]:
		gridmap.set_cell_item(cell, 0)
	for group in ["Trees", "Rocks", "Grass"]:
		meadow.get_node(group).visible = false

if EXTRAS_ON and not STAGE_ON:
	for step in range(9, 19):
		gridmap.set_cell_item(Vector3i(step, 0, -6), 3)
	for cell in [Vector3i(-14, 0, 2), Vector3i(-13, 0, 3), Vector3i(12, 0, 4), Vector3i(13, 0, 5)]:
		gridmap.set_cell_item(cell, 3)
	for cell in [Vector3i(0, 0, -6), Vector3i(1, 0, -6)]:
		gridmap.set_cell_item(cell, 0)

var bank_path := "res://art/water/bank_kit.glb"
if BANK_ON and FileAccess.file_exists(bank_path):
	var document := GLTFDocument.new()
	var state := GLTFState.new()
	document.append_from_file(ProjectSettings.globalize_path(bank_path), state)
	var kit: Node = document.generate_scene(state)
	var bank_material := ShaderMaterial.new()
	bank_material.shader = load("res://art/shaders/bank.gdshader")
	bank_material.set_shader_parameter("dirt_texture", load("res://art/ground/dirt_albedo.png"))
	bank_material.set_shader_parameter("ground_texture", ground.get_shader_parameter("albedo_texture"))
	bank_material.set_shader_parameter("ground_tint", ground.get_shader_parameter("albedo_tint"))
	bank_material.set_shader_parameter("edge_noise", ground.get_shader_parameter("edge_noise"))
	var clod_noise := FastNoiseLite.new()
	clod_noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	clod_noise.frequency = 0.03
	clod_noise.fractal_octaves = 3
	var clod_height := NoiseTexture2D.new()
	clod_height.noise = clod_noise
	clod_height.seamless = true
	clod_height.width = 256
	clod_height.height = 256
	var clod_normals := NoiseTexture2D.new()
	clod_normals.noise = clod_noise
	clod_normals.seamless = true
	clod_normals.as_normal_map = true
	clod_normals.bump_strength = 5.0
	clod_normals.width = 256
	clod_normals.height = 256
	await clod_normals.changed
	bank_material.set_shader_parameter("clod_height", clod_height)
	bank_material.set_shader_parameter("clod_normals", clod_normals)
	var library := MeshLibrary.new()
	var kinds := ["bank_straight", "bank_water_corner", "bank_land_corner", "bank_diagonal"]
	var variants := {}
	var slot := 0
	for kind in kinds:
		variants[kind] = []
		for letter in ["a", "b", "c"]:
			var piece: MeshInstance3D = kit.find_child("%s_%s" % [kind, letter], true, false)
			if piece == null:
				continue
			library.create_item(slot)
			library.set_item_mesh(slot, piece.mesh)
			piece.mesh.surface_set_material(0, bank_material)
			variants[kind].append(slot)
			slot += 1
	var bank := GridMap.new()
	bank.mesh_library = library
	bank.cell_size = Vector3(0.5, 0.5, 0.5)
	bank.cell_center_y = false
	bank.position = Vector3(-0.25, 0.0, -0.25)
	meadow.add_child(bank)
	# The water among the four cells around each corner, as quadrants: x then z, 0 for the low side.
	var canonical := {
		"bank_straight": [[0, 1], [1, 1]],
		"bank_water_corner": [[1, 1]],
		"bank_land_corner": [[0, 1], [1, 0], [1, 1]],
		"bank_diagonal": [[0, 1], [1, 0]],
	}
	var table := {}
	for item in canonical:
		for turn in 4:
			var cells := []
			for q in canonical[item]:
				var p := Vector2(q[0] - 0.5, q[1] - 0.5)
				for k in turn:
					p = Vector2(p.y, -p.x)
				cells.append(int(p.x > 0) * 2 + int(p.y > 0))
			cells.sort()
			table[cells] = [item, turn]
	var count := 0
	for a in range(-61, 61):
		for b in range(-61, 61):
			var water := []
			for qx in 2:
				for qz in 2:
					if gridmap.get_cell_item(Vector3i(a - 1 + qx, 0, b - 1 + qz)) == 3:
						water.append(qx * 2 + qz)
			water.sort()
			if table.has(water):
				var entry = table[water]
				var options: Array = variants[entry[0]]
				bank.set_cell_item(Vector3i(a, 0, b), options[posmod(a * 7 + b * 13, options.size())], bank.get_orthogonal_index_from_basis(Basis(Vector3.UP, entry[1] * PI / 2.0)))
				count += 1
	print("[proto] banks placed %s" % count)

for block in meadow.get_node("Grass").get_children():
	var multimesh: MultiMesh = block.multimesh
	for i in multimesh.instance_count:
		var t := multimesh.get_instance_transform(i)
		if gridmap.get_cell_item(gridmap.local_to_map(t.origin)) == 3:
			multimesh.set_instance_transform(i, Transform3D(Basis.from_scale(Vector3.ZERO), t.origin))
var moved := []
for group in ["Trees", "Rocks"]:
	for node in meadow.get_node(group).get_children():
		var offset := (Vector2(node.global_position.x, node.global_position.z) - center) / Vector2(5.4, 4.2)
		if offset.length() < 1.0:
			if group == "Trees":
				moved.append(node)
			else:
				node.visible = false
# Trees on the far and east shore, so the water has something to reflect.
var shore := [Vector3(-2.6, 0, -6.3), Vector3(1.4, 0, -6.6), Vector3(4.9, 0, -3.8), Vector3(-5.3, 0, -3.6), Vector3(3.0, 0, -6.0)]
for i in moved.size():
	if i < shore.size():
		moved[i].global_position = shore[i]
	else:
		moved[i].visible = false
meadow.get_node("Player").global_position = Vector3(center.x, 0.0, center.y + 5.0)
print("[proto] pond painted %s %s %s" % [water_material.shader.get_shader_uniform_list().size(), bed_material.shader.get_shader_uniform_list().size(), mesh.get_surface_count()])
'''


def zoom(size):
    return {'op': 'eval', 'code': f'tree.root.get_node("Meadow/CameraRig").get("Camera").size = {size}'}


def hour(time, name, size=20.0):
    return [{'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", {time})'}, zoom(size),
            {'op': 'wait', 'frames': 60}, {'op': 'capture', 'name': f'{PREFIX}_{name}', 'frames': 10}]


def spots():
    if os.environ.get('STAGE', '0') != '1':
        return []
    out = []
    # (name, x, z) of the thing to look at, in meters; the player stands 2.5 m south so the camera centers above it.
    for name, x, z, size in [('lake', -3.0, -2.5, 8.0), ('wall', -4.0, -4.6, 2.6), ('wall_south', -3.0, -1.6, 2.6)]:
        out += [{'op': 'eval', 'code': f'var meadow := tree.root.get_node("Meadow")\nmeadow.get_node("Player").global_position = Vector3({x}, 0.0, {z + (2.5 if size > 5 else 0.9)})\nvar clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", 0.5)'},
                zoom(size), {'op': 'wait', 'frames': 50}, {'op': 'capture', 'name': f'{PREFIX}_spot_{name}', 'frames': 10}]
    return out


PREFIX = os.environ.get('PREFIX', 'protow')
STAGE_ON = os.environ.get('STAGE', '0') == '1'
EXTRAS_ON = os.environ.get('EXTRAS', '0') == '1'
BANK_ON = os.environ.get('BANK', '1') == '1'
pond_x, pond_z = os.environ.get('POND_X', '0'), os.environ.get('POND_Z', '-3')
out_dir = os.path.dirname(sys.argv[2])
game = game_steps(os.path.join(out_dir, 'game-protow.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    eval_(POND.replace('STAGE_ON', 'true' if STAGE_ON else 'false').replace('EXTRAS_ON', 'true' if EXTRAS_ON else 'false').replace('BANK_ON', 'true' if BANK_ON else 'false').replace('POND_X', pond_x).replace('POND_Z', pond_z)),
    {'op': 'wait', 'frames': 40},
    {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)'},
    *hour(0.5, 'noon'), *hour(0.5, 'noon_close', 11.0), *hour(0.5, 'noon_max', 8.0), *hour(0.75, 'dusk', 11.0), *hour(0.0, 'night', 11.0), *spots(),
    {'op': 'quit'}])
steps = [{'op': 'sleep', 'seconds': 15}, *play(game, 90, capture_output='protow_output')]
write(sys.argv[2], steps)
