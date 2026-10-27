# Prototype: the four bank pieces, built from a signed distance to the land (inland distance s, 0 at the waterline).
import bpy, bmesh, math, sys
from mathutils import Vector

WALL = 0.2        # the waterline lies this far into the water cell
HALF = 0.25       # half of a dual cell
TOP_Y = 0.012     # above the ground layers
BED_Y = -0.75
BORDER = 0.3     # the dirt border reaches this far from the waterline
STEP = 0.0313
# Rows down the wall, evenly under the lip, so the shader's lumps have vertices to move.
ROWS = [(0.0, 0.0)] + [(-0.0583 * k, 0.0) for k in range(1, 7)] + [(-0.5, 0.0), (-0.75, 0.0)]

def box_distance(px, pz, x0, x1, z0, z1):
    dx = max(x0 - px, 0.0, px - x1)
    dz = max(z0 - pz, 0.0, pz - z1)
    return math.hypot(dx, dz)

# Quadrant boxes by (sign x, sign z), as ranges in a 1.0 m window around the corner.
QUAD = {(-1, -1): (-1, 0, -1, 0), (1, -1): (0, 1, -1, 0), (-1, 1): (-1, 0, 0, 1), (1, 1): (0, 1, 0, 1)}

ROUND = 0.05      # radius of the rounded water corners: the arc must end inside the piece

def sd_box(px, pz, x0, x1, z0, z1):
    cx, cz, hx, hz = (x0 + x1) / 2, (z0 + z1) / 2, (x1 - x0) / 2, (z1 - z0) / 2
    qx, qz = abs(px - cx) - hx, abs(pz - cz) - hz
    return math.hypot(max(qx, 0.0), max(qz, 0.0)) + min(max(qx, qz), 0.0)

def inland(px, pz, land):
    # Land cells dilated by WALL, with the water corners rounded: the water is the cells that are not land, shrunk by
    # WALL + ROUND, then grown by ROUND.
    water = [q for q in QUAD if q not in land]
    if not water:
        return 1.0
    if len(land) == 1:
        return WALL - box_distance(px, pz, *QUAD[land[0]])
    inner = []
    for q in water:
        x0, x1, z0, z1 = QUAD[q]
        # Shrink toward the quadrant's far side by WALL + ROUND on the sides that touch land.
        sx, sz = (1 if q[0] > 0 else -1), (1 if q[1] > 0 else -1)
        nx0 = x0 + (WALL + ROUND if sx > 0 and (-1, q[1]) in land else 0) if sx > 0 else x0
        nx1 = x1 - (WALL + ROUND if sx < 0 and (1, q[1]) in land else 0) if sx < 0 else x1
        nz0 = z0 + (WALL + ROUND if sz > 0 and (q[0], -1) in land else 0) if sz > 0 else z0
        nz1 = z1 - (WALL + ROUND if sz < 0 and (q[0], 1) in land else 0) if sz < 0 else z1
        inner.append((nx0, nx1, nz0, nz1))
    return min(sd_box(px, pz, *box) for box in inner) - ROUND

def lattice(ix, iy, iz, seed):
    h = (ix * 374761393 + iy * 668265263 + iz * 2147483647 + seed * 1274126177) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return (h & 0xFFFF) / 32767.5 - 1.0

def value3(x, y, z, seed):
    fx, fy, fz = math.floor(x), math.floor(y), math.floor(z)
    tx, ty, tz = x - fx, y - fy, z - fz
    tx, ty, tz = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty), tz * tz * (3 - 2 * tz)
    def corner(dx, dy, dz):
        return lattice(int(fx) + dx, int(fy) + dy, int(fz) + dz, seed)
    def mix(a, b, k):
        return a + (b - a) * k
    return mix(mix(mix(corner(0, 0, 0), corner(1, 0, 0), tx), mix(corner(0, 1, 0), corner(1, 1, 0), tx), ty),
               mix(mix(corner(0, 0, 1), corner(1, 0, 1), tx), mix(corner(0, 1, 1), corner(1, 1, 1), tx), ty), tz)

def smoothstep(a, b, x):
    k = min(max((x - a) / (b - a), 0.0), 1.0)
    return k * k * (3 - 2 * k)

BUMP = 0.15       # how far the face moves, in meters
EDGE_CALM = 0.07   # the face is flat this close to a piece's edge, so neighbors meet

def displace(x, z, y, weight, seed):
    # Lumps and hollows, from two octaves of noise, zero at the piece's edge so every variant meets every neighbor.
    window = smoothstep(0.0, EDGE_CALM, HALF - max(abs(x), abs(z)))
    n = (0.38 * value3(x / 0.3, y / 0.2, z / 0.3, seed) + 0.34 * value3(x / 0.15, y / 0.1, z / 0.15, seed + 101)
         + 0.28 * value3(x / 0.075, y / 0.05, z / 0.075, seed + 202))
    return BUMP * window * weight * (0.4 + 0.8 * max(min(n * 1.9, 1.0), -1.0))

def gradient(px, pz, land):
    e = 1e-4
    gx = (inland(px + e, pz, land) - inland(px - e, pz, land)) / (2 * e)
    gz = (inland(px, pz + e, land) - inland(px, pz - e, land)) / (2 * e)
    length = math.hypot(gx, gz) or 1.0
    return gx / length, gz / length

def clip(poly, lo, hi):
    # poly: list of (x, z, s); keep lo <= s <= hi
    for bound, keep_above in ((lo, True), (hi, False)):
        out = []
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]
            ina = (a[2] >= bound) if keep_above else (a[2] <= bound)
            inb = (b[2] >= bound) if keep_above else (b[2] <= bound)
            if ina:
                out.append(a)
            if ina != inb:
                t = (bound - a[2]) / (b[2] - a[2])
                out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, bound))
        poly = out
        if len(poly) < 3:
            return []
    return poly

def build(name, land, seed):
    verts, faces, colors = [], [], []
    def oriented(ids, want):
        # Newell normal in Blender coordinates; flip the loop when it opposes the wanted direction.
        nx = ny = nz = 0.0
        for k in range(len(ids)):
            a, b = verts[ids[k]], verts[ids[(k + 1) % len(ids)]]
            nx += (a[1] - b[1]) * (a[2] + b[2])
            ny += (a[2] - b[2]) * (a[0] + b[0])
            nz += (a[0] - b[0]) * (a[1] + b[1])
        return ids if nx * want[0] + ny * want[1] + nz * want[2] >= 0 else ids[::-1]
    index = {}
    def vert(x, z, y, face_mask, s):
        key = (round(x, 5), round(z, 5), round(y, 5), face_mask)
        if key not in index:
            index[key] = len(verts)
            gx, gz = gradient(x, z, land)
            weight = 1.0 if face_mask > 0.5 or s <= 1e-6 else max(1.0 - s / 0.1, 0.0)
            move = displace(x, z, y, weight, seed)
            verts.append((x - gx * move, -(z - gz * move), y))  # Blender y = -Godot z, Blender z = height
            colors.append((face_mask, min(max(s / BORDER, 0.0), 1.0), 0.0, 1.0))
        return index[key]
    n = int(2 * HALF / STEP + 0.5)
    segments = []
    def top_y(s):
        return TOP_Y - 0.05 * (1.0 - min(max(s / 0.09, 0.0), 1.0)) ** 2
    for i in range(n):
        for j in range(n):
            xs = [-HALF + i * STEP, -HALF + (i + 1) * STEP]
            zs = [-HALF + j * STEP, -HALF + (j + 1) * STEP]
            corners = [(xs[0], zs[0]), (xs[1], zs[0]), (xs[1], zs[1]), (xs[0], zs[1])]
            poly = [(x, z, inland(x, z, land)) for x, z in corners]
            poly = clip(poly, 0.0, BORDER)
            if not poly:
                continue
            ids = [vert(x, z, top_y(s), 0.0, s) for x, z, s in poly]
            faces.append(oriented(ids, (0, 0, 1)))
            for k in range(len(poly)):
                a, b = poly[k], poly[(k + 1) % len(poly)]
                if abs(a[2]) < 1e-6 and abs(b[2]) < 1e-6:
                    segments.append((a, b))
    # The wall: each waterline segment dropped to the bed in rows, bumped by noise.
    for a, b in segments:
        rows = []
        for end in (a, b):
            gx, gz = gradient(end[0], end[1], land)
            column = []
            for k, (y, bump) in enumerate(ROWS):
                out = (-gx, -gz)  # toward the water
                column.append(vert(end[0], end[1], y if k else top_y(0.0), 1.0 if k else 0.0, 0.0))
            rows.append(column)
        for k in range(len(ROWS) - 1):
            mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            gx, gz = gradient(mid[0], mid[1], land)
            faces.append(oriented([rows[0][k], rows[1][k], rows[1][k + 1], rows[0][k + 1]], (-gx, gz, 0.0)))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    layer = mesh.color_attributes.new('Color', 'FLOAT_COLOR', 'POINT')
    for i, c in enumerate(colors):
        layer.data[i].color = c
    mesh.shade_smooth() if hasattr(mesh, 'shade_smooth') else None
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj

bpy.ops.wm.read_factory_settings(use_empty=True)
PIECES = {
    'bank_straight': ([(-1, -1), (1, -1)], 3),
    'bank_water_corner': ([(-1, -1), (1, -1), (-1, 1)], 2),
    'bank_land_corner': ([(-1, -1)], 2),
    'bank_diagonal': ([(-1, -1), (1, 1)], 2),
}
for name, (land, variants) in PIECES.items():
    for variant in range(variants):
        obj = build(f'{name}_{"abc"[variant]}', land, 17 + 31 * variant)
        print(obj.name, len(obj.data.vertices), len(obj.data.polygons))
bpy.ops.export_scene.gltf(filepath=sys.argv[-1], export_format='GLB', export_vertex_color='ACTIVE', export_attributes=True)
