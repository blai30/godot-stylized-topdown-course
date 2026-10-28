# Prototype: a world generated from noise in the meadow's own systems, to judge the look before any lesson is written.
import os
import sys
sys.path.insert(0, sys.argv[1])
from steps import write, eval_, game_steps, play

CLOCK = 'Meadow/WorldEnvironment/Day'
PREFIX = os.environ.get('PREFIX', 'protog')
SEED = os.environ.get('SEED', '7')

GENERATE = '''
var started := Time.get_ticks_msec()
var meadow := tree.root.get_node("Meadow")
var ground: GridMap = meadow.get_node("GroundTiles")
var bank: GridMap = meadow.get_node("Bank")
ground.clear()
bank.clear()
for group in ["Trees", "Rocks", "Patches"]:
	for node in meadow.get_node(group).get_children():
		node.free()

var seed_value := SEED_VALUE
var terrain := FastNoiseLite.new()
terrain.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
terrain.fractal_type = FastNoiseLite.FRACTAL_FBM
terrain.fractal_octaves = 3
terrain.frequency = 0.04
terrain.seed = seed_value
var patches := FastNoiseLite.new()
patches.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
patches.frequency = 0.1
patches.seed = seed_value + 1
var forest := FastNoiseLite.new()
forest.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
forest.fractal_type = FastNoiseLite.FRACTAL_FBM
forest.fractal_octaves = 2
forest.frequency = 0.07
forest.seed = seed_value + 2

var half := 48
var cells := {}
for cx in range(-half, half):
	for cz in range(-half, half):
		var p := (Vector2(cx, cz) + Vector2(0.5, 0.5)) * 0.5
		var n := terrain.get_noise_2d(p.x, p.y)
		var item := 0
		if n < WATER_BELOW and maxf(absf(cx + 0.5), absf(cz + 0.5)) < half - 4:
			item = 3
		cells[Vector2i(cx, cz)] = item

# Water narrower than three cells becomes sand.
var run := func(cell: Vector2i, direction: Vector2i) -> int:
	var count := 1
	var next: Vector2i = cell + direction
	while cells.get(next, 0) == 3:
		count += 1
		next += direction
	next = cell - direction
	while cells.get(next, 0) == 3:
		count += 1
		next -= direction
	return count
for pass_index in 3:
	var narrow := []
	for cell in cells:
		if cells[cell] == 3 and mini(run.call(cell, Vector2i.RIGHT), run.call(cell, Vector2i.DOWN)) < 3:
			narrow.append(cell)
	for cell in narrow:
		cells[cell] = 0
for cell in cells:
	ground.set_cell_item(Vector3i(cell.x, 0, cell.y), cells[cell])

var counts := [0, 0, 0, 0]
for cell in cells:
	counts[cells[cell]] += 1
print("[proto] cells grass %s sand %s dirt %s water %s" % counts)

bank.call("UpdateShore")

# How far a cell is from water, in cells, up to a limit.
var near_water := func(cell: Vector2i, limit: int) -> int:
	for radius in range(1, limit + 1):
		for dx in range(-radius, radius + 1):
			for dz in range(-radius, radius + 1):
				if maxi(absi(dx), absi(dz)) == radius and cells.get(cell + Vector2i(dx, dz), 0) == 3:
					return radius
	return limit + 1

var oak: PackedScene = load("res://art/nature/tree_oak/tree_oak.tscn")
var pine: PackedScene = load("res://art/nature/tree_pine/tree_pine.tscn")
var rock_small: PackedScene = load("res://art/nature/rock_small/rock_small.tscn")
var rock_large: PackedScene = load("res://art/nature/rock_large/rock_large.tscn")
var placed := []
var spacing_ok := func(point: Vector2, spacing: float) -> bool:
	for other in placed:
		if point.distance_to(other) < spacing:
			return false
	return true
var trees := 0
var rocks := 0
var random := RandomNumberGenerator.new()
random.seed = seed_value
var step := 2
for gx in range(-half, half, step):
	for gz in range(-half, half, step):
		var cell := Vector2i(gx, gz) + Vector2i(random.randi_range(0, step - 1), random.randi_range(0, step - 1))
		var point := (Vector2(cell) + Vector2(0.5, 0.5)) * 0.5
		var roll := random.randf()
		var kind := random.randf()
		var density := clampf(remap(forest.get_noise_2d(point.x, point.y), TREE_FROM, TREE_TO, 0.0, 1.0), 0.0, 1.0)
		if cells.get(cell, 3) != 0 or roll > density or absi(cell.x) > half - 5 or absi(cell.y) > half - 5:
			continue
		if near_water.call(cell, 4) <= 3 or not spacing_ok.call(point, 2.0):
			continue
		var tree_node: Node3D = (pine if kind < 0.4 else oak).instantiate()
		tree_node.position = Vector3(point.x, 0.0, point.y)
		tree_node.rotation.y = random.randf() * TAU
		tree_node.scale = Vector3.ONE * random.randf_range(0.85, 1.2)
		meadow.get_node("Trees").add_child(tree_node)
		placed.append(point)
		trees += 1

# Rocks on the shore and in the open, a few at a time.
for gx in range(-half, half, 3):
	for gz in range(-half, half, 3):
		var cell := Vector2i(gx, gz) + Vector2i(random.randi_range(0, 2), random.randi_range(0, 2))
		var point := (Vector2(cell) + Vector2(0.5, 0.5)) * 0.5
		var roll := random.randf()
		var kind := random.randf()
		var distance: int = near_water.call(cell, 6)
		var chance := 0.0
		if cells.get(cell, 3) == 3 or roll > chance or absi(cell.x) > half - 5 or absi(cell.y) > half - 5:
			continue
		if distance < 3 or not spacing_ok.call(point, 2.5):
			continue
		var rock: Node3D = (rock_large if kind < 0.3 else rock_small).instantiate()
		rock.position = Vector3(point.x, 0.0, point.y)
		rock.rotation.y = random.randf() * TAU
		meadow.get_node("Rocks").add_child(rock)
		placed.append(point)
		rocks += 1

# The water plane covers the level.
var water_node: Node3D = meadow.get_node("Water")
water_node.scale = Vector3(48.0 / 19.6, 1.0, 48.0 / 19.6)

meadow.get_node("Grass").call("Scatter")
print("[proto] trees %s rocks %s in %s ms" % [trees, rocks, Time.get_ticks_msec() - started])
'''


def zoom(size):
    return {'op': 'eval', 'code': f'tree.root.get_node("Meadow/CameraRig").get("Camera").size = {size}'}


def hour(time, name, size=20.0):
    return [{'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("TimeOfDay", {time})'}, zoom(size),
            {'op': 'wait', 'frames': 60}, {'op': 'capture', 'name': f'{PREFIX}_{name}', 'frames': 10}]


def stand(name, x, z, size, time=0.5):
    code = f'''
var meadow := tree.root.get_node("Meadow")
var ground: GridMap = meadow.get_node("GroundTiles")
var best := Vector3({x}, 0.0, {z})
var best_distance := 1e9
for cell in ground.get_used_cells():
	if ground.get_cell_item(cell) == 0:
		var point := ground.map_to_local(cell)
		var distance := point.distance_to(Vector3({x}, 0.0, {z}))
		if distance < best_distance:
			best_distance = distance
			best = point
meadow.get_node("Player").global_position = Vector3(best.x, 0.0, best.z + 2.0)
var clock := tree.root.get_node("{CLOCK}")
clock.set("TimeOfDay", {time})
'''
    return [eval_(code), zoom(size), {'op': 'wait', 'frames': 70}, {'op': 'capture', 'name': f'{PREFIX}_{name}', 'frames': 10}]


out_dir = os.path.dirname(sys.argv[2])
code = (GENERATE.replace('SEED_VALUE', SEED)
        .replace('WATER_BELOW', os.environ.get('WATER_BELOW', '-0.25'))
        .replace('SAND_BELOW', os.environ.get('SAND_BELOW', '-0.15'))
        .replace('TREE_FROM', os.environ.get('TREE_FROM', '0.0'))
        .replace('TREE_TO', os.environ.get('TREE_TO', '0.5')))
game = game_steps(os.path.join(out_dir, 'game-protog.jsonl'), [
    {'op': 'wait', 'frames': 60}, {'op': 'sleep', 'seconds': 4},
    eval_(code),
    {'op': 'wait', 'frames': 60},
    {'op': 'eval', 'code': f'var clock := tree.root.get_node("{CLOCK}")\nclock.set("Running", false)'},
    *stand('wide', 0.0, 0.0, 60.0),
    *stand('nw', -12.0, -12.0, 20.0), *stand('ne', 12.0, -12.0, 20.0),
    *stand('sw', -12.0, 12.0, 20.0), *stand('se', 12.0, 12.0, 20.0),
    *stand('close', 0.0, 0.0, 11.0), *hour(0.75, 'dusk', 20.0),
    {'op': 'quit'}])
steps = [{'op': 'sleep', 'seconds': 15}, *play(game, 120, capture_output='protog_output')]
write(sys.argv[2], steps)
