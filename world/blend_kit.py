# Headless Blender: build the world's building/prop kit with real geometric detail and
# ambient occlusion baked into vertex colours, export ONE GLB whose objects are named.
# The world's merge batcher (mp/mbStart/mbEnd in index.html) eats these geometries, so
# every bit of detail here costs triangles only - never a draw call.
#
# COLOR_0 convention (read by the patched mp()):
#   rgb = ao * partColour, a = 1 -> "body, tint me with the palette colour passed from JS"
#   rgb = ao * partColour, a = 0 -> "accent, keep my own colour"
#
# Blender is Z-up; the glTF exporter converts to Y-up. Everything below is built with z = height,
# base at z = 0, centred in x/y, at the nominal size the JS builders scale from.
#
# run: blender -b -P blend_kit.py -- models/kit.glb
import bpy, sys, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

OUT = (sys.argv[sys.argv.index('--')+1:] or ['kit.glb'])[0]
TAU = math.pi*2

# ---- palette (same hexes the world already uses) -> 0..1 tuples ----
def H(h): return ((h >> 16 & 255)/255.0, (h >> 8 & 255)/255.0, (h & 255)/255.0)
GLASS  = H(0x64879e); GLASS2 = H(0x7a9bb0); DARK = H(0x6b7b8a); METAL = H(0x9aa6b3)
MAROON = H(0x8a1c2b); GOLD   = H(0xf0b323)
WOOD   = H(0x7a4b2a); WOOD2  = H(0x6e4a2a); NIPA = H(0xa9814f); BAMBOO = H(0xc8a878)
LEAF   = H(0x3f8f45); LEAF2  = H(0x2f7a38); PALM = H(0x4a9a52); TRUNK = H(0x9a6b3a)
ASPH   = H(0x2f3b45); WHITE  = (1.0, 1.0, 1.0); LAMP = H(0xfff2b0); STONE = H(0x8b8a86)
RED    = H(0xc0392b); TYRE   = H(0x222222); CREAM = H(0xfbf7f1); SKYBLU = H(0x6fb7e6)

# ---- geometry accumulation for the archetype being built ----
V = []; F = []; C = []
def reset():
    global V, F, C
    V = []; F = []; C = []

def emit(vs, fs, col, tint):
    n = len(V)
    V.extend(vs)
    F.extend([tuple(n+i for i in f) for f in fs])
    C.extend([(col[0], col[1], col[2], float(tint))]*len(vs))

def box(x, y, z, w, d, h, col, tint=1, rz=0.0):
    """centre x,y - base-relative centre z - size w(x) d(y) h(z), rotated rz about z"""
    hw, hd, hh = w/2.0, d/2.0, h/2.0
    pts = [(-hw,-hd,-hh),(hw,-hd,-hh),(hw,hd,-hh),(-hw,hd,-hh),
           (-hw,-hd, hh),(hw,-hd, hh),(hw,hd, hh),(-hw,hd, hh)]
    ca, sa = math.cos(rz), math.sin(rz)
    vs = [(x + p[0]*ca - p[1]*sa, y + p[0]*sa + p[1]*ca, z + p[2]) for p in pts]
    fs = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    emit(vs, fs, col, tint)

def cyl(x, y, z, rb, rt, h, seg, col, tint=1, rz=0.0):
    vs = []; fs = []
    for r, zz in ((rb, -h/2.0), (rt, h/2.0)):
        for i in range(seg):
            a = i/float(seg)*TAU + rz
            vs.append((x + math.cos(a)*r, y + math.sin(a)*r, z + zz))
    for i in range(seg):
        j = (i+1) % seg
        fs.append((i, j, seg+j, seg+i))
    vs.append((x, y, z - h/2.0)); vs.append((x, y, z + h/2.0))
    cb, ct = len(vs)-2, len(vs)-1
    for i in range(seg):
        j = (i+1) % seg
        if rb > 1e-5: fs.append((cb, j, i))
        if rt > 1e-5: fs.append((ct, seg+i, seg+j))
    emit(vs, fs, col, tint)

def cone(x, y, z, r, h, seg, col, tint=1, rz=0.0):
    cyl(x, y, z, r, 0.0, h, seg, col, tint, rz)

def prism(x, y, z, w, d, h, col, tint=1):
    """triangular prism (roof ridge) running along x"""
    hw, hd = w/2.0, d/2.0
    vs = [(x-hw, y-hd, z), (x+hw, y-hd, z), (x+hw, y+hd, z), (x-hw, y+hd, z),
          (x-hw, y, z+h), (x+hw, y, z+h)]
    fs = [(0,3,2,1), (0,1,5,4), (2,3,4,5), (1,2,5), (3,0,4)]
    emit(vs, fs, col, tint)

# ---- ribbed facade: the detail that stops a tower reading as a striped box ----
def facade(w, d, h, floors, body, glass, podium=True):
    fh = h/float(floors)
    ins = min(0.20, w*0.085)
    for i in range(floors):
        z0 = i*fh
        box(0, 0, z0 + fh*0.23, w, d, fh*0.46, body, 1)                       # spandrel band
        box(0, 0, z0 + fh*0.73, w-ins*2, d-ins*2, fh*0.54, glass, 0)          # recessed glazing
        box(0, 0, z0 + fh*0.99, w-ins*0.6, d-ins*0.6, fh*0.06, body, 1)       # lintel over the reveal
    # mullions sit ON each face, in the reveal - spanning the full depth would skin the building shut
    n = max(2, int(w/0.9)); m = max(2, int(d/0.9))
    for k in range(1, n):
        mx = -w/2.0 + k*(w/float(n))
        for sy in (-1, 1): box(mx, sy*(d/2.0 - ins*0.5), h/2.0, 0.10, ins*1.05, h, body, 1)
    for k in range(1, m):
        my = -d/2.0 + k*(d/float(m))
        for sx in (-1, 1): box(sx*(w/2.0 - ins*0.5), my, h/2.0, ins*1.05, 0.10, h, body, 1)
    for sx in (-1, 1):                                                         # corner piers
        for sy in (-1, 1): box(sx*(w/2.0-0.07), sy*(d/2.0-0.07), h/2.0, 0.14, 0.14, h, body, 1)
    if podium:
        box(0, 0, fh*0.55, w+0.34, d+0.34, fh*1.1, body, 1)                    # base podium
        box(0, -(d/2.0+0.30), fh*0.95, w*0.5, 0.62, 0.1, DARK, 0)              # entrance canopy
        box(0, -(d/2.0+0.02), fh*0.45, w*0.34, 0.08, fh*0.8, GLASS, 0)         # doors

def roofplant(w, d, tall=True):
    box(0, 0, 0.16, w+0.30, d+0.30, 0.32, DARK, 0)                             # parapet
    box(w*0.16, d*0.12, 0.55, w*0.34, d*0.34, 0.7, DARK, 0)                    # machine room
    box(-w*0.22, -d*0.18, 0.36, w*0.22, d*0.26, 0.32, METAL, 0)                # AC unit
    cyl(-w*0.18, d*0.22, 0.5, 0.17, 0.17, 0.6, 8, METAL, 0)                    # water tank
    if tall:
        cyl(w*0.16, d*0.12, 1.85, 0.05, 0.03, 1.9, 6, METAL, 0)                # mast
        box(w*0.16, d*0.12, 2.4, 0.28, 0.05, 0.05, RED, 0)

# ---- ambient occlusion, raycast against the archetype itself + an implicit ground ----
AO_RAYS = [None]
def hemi(n):
    """cosine-ish hemisphere directions around +z, computed once"""
    out = []
    for i in range(n):
        t = (i + 0.5)/n
        z = math.sqrt(1.0 - t*0.85)
        r = math.sqrt(max(0.0, 1.0 - z*z))
        a = i*2.399963
        out.append(Vector((math.cos(a)*r, math.sin(a)*r, z)))
    return out

def bake_ao(strength=0.45, dist=0.55, floor=0.6):
    """per-vertex AO from self-occlusion plus contact darkening at the ground plane"""
    tris = []
    for f in F:
        tris.append((f[0], f[1], f[2]))
        if len(f) == 4: tris.append((f[0], f[2], f[3]))
    bvh = BVHTree.FromPolygons([Vector(v) for v in V], tris, all_triangles=True, epsilon=0.0)
    nrm = [Vector((0.0, 0.0, 0.0)) for _ in V]
    for a, b, c in tris:
        va, vb, vc = Vector(V[a]), Vector(V[b]), Vector(V[c])
        fn = (vb-va).cross(vc-va)
        for i in (a, b, c): nrm[i] += fn
    if AO_RAYS[0] is None: AO_RAYS[0] = hemi(12)
    rays = AO_RAYS[0]
    for i, v in enumerate(V):
        n = nrm[i]
        n = n.normalized() if n.length > 1e-9 else Vector((0.0, 0.0, 1.0))
        up = Vector((0.0, 0.0, 1.0)) if abs(n.z) < 0.95 else Vector((1.0, 0.0, 0.0))
        t1 = n.cross(up).normalized(); t2 = n.cross(t1)
        o = Vector(v) + n*0.012
        hits = 0.0
        for r in rays:
            d = (t1*r.x + t2*r.y + n*r.z).normalized()
            if d.z < 0 and o.z > 1e-4 and (-o.z/d.z) < dist:
                hits += 1.0; continue                       # the ground plane at z = 0
            hit = bvh.ray_cast(o, d, dist)
            if hit[0] is not None: hits += 1.0 - (hit[3]/dist)*0.5
        ao = max(floor, 1.0 - (hits/len(rays))*strength)   # a floor keeps crevices readable, not muddy
        r0, g0, b0, a0 = C[i]
        C[i] = (r0*ao, g0*ao, b0*ao, a0)

# ---- turn the accumulated lists into a named Blender object ----
def finish(name, ao=True):
    if ao: bake_ao()
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in V], [], [list(f) for f in F])
    me.validate(); me.update()
    ca = me.color_attributes.new(name='Col', type='FLOAT_COLOR', domain='POINT')
    for i, c in enumerate(C): ca.data[i].color = (c[0], c[1], c[2], c[3])
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    for p in me.polygons: p.use_smooth = False
    print('  %-12s %5d verts %5d faces' % (name, len(V), len(F)))
    reset()
    return ob

# =====================================================================================
bpy.ops.wm.read_factory_settings(use_empty=True)
print('building kit...')

# --- skyscrapers: nominal 3 wide x 12 tall, JS scales (w/3, h/12, w/3) ---
facade(3.0, 3.0, 8.4, 7, WHITE, GLASS); box(0, 0, 9.6, 2.1, 2.1, 2.4, WHITE, 1)
box(0, 0, 10.9, 2.16, 2.16, 0.2, DARK, 0); box(0, 0, 11.6, 1.2, 1.2, 1.2, WHITE, 1)
finish('sky_a')                                                   # stepped-back tower

facade(3.0, 3.0, 11.0, 9, WHITE, GLASS2)
box(0, 0, 11.3, 3.3, 3.3, 0.35, WHITE, 1)                          # cornice
finish('sky_b')                                                    # flat slab, strong cornice

facade(2.6, 3.4, 10.2, 8, WHITE, GLASS)
for s in (-1, 1): box(s*1.45, 0, 5.6, 0.34, 3.5, 11.2, WHITE, 1)   # corner piers
box(0, 0, 11.5, 1.5, 2.2, 1.4, WHITE, 1)
finish('sky_c')                                                    # piered tower

roofplant(3.0, 3.0, True);  finish('sky_top_a')
roofplant(3.0, 3.0, False); finish('sky_top_b')

# --- mid-rise: nominal 4 wide x 6 tall ---
fh = 6.0/4
for i in range(4):
    z0 = i*fh
    box(0, 0, z0+fh*0.22, 4.0, 4.0, fh*0.44, WHITE, 1)
    box(0, 0, z0+fh*0.72, 3.7, 3.7, fh*0.56, GLASS, 0)
    box(0, -2.08, z0+fh*0.62, 3.2, 0.22, fh*0.42, WHITE, 1)        # balcony slab
    box(0, -2.18, z0+fh*0.86, 3.2, 0.06, 0.34, METAL, 0)           # railing
box(0, 0, 6.18, 4.4, 4.4, 0.36, WHITE, 1)
cyl(1.2, 1.0, 6.75, 0.34, 0.34, 0.8, 8, METAL, 0)
box(-1.1, 0.9, 6.6, 0.9, 0.9, 0.5, DARK, 0)
finish('mid_a')

# --- Philippine shophouse: nominal 4 wide x 3.4 tall ---
box(0, 0, 1.7, 4.0, 3.6, 3.4, WHITE, 1)
box(0, -1.86, 0.95, 3.4, 0.12, 1.9, GLASS, 0)                      # shopfront glazing
box(0, -1.95, 2.35, 4.2, 0.18, 0.7, MAROON, 0)                     # signage board
box(0, -2.25, 2.02, 4.0, 0.7, 0.06, CREAM, 0)                      # awning
for s in (-1.6, 1.6): cyl(s, -2.5, 1.0, 0.05, 0.05, 2.0, 6, METAL, 0)
box(1.35, -1.86, 2.8, 0.7, 0.3, 0.5, METAL, 0)                     # aircon box
box(0, 0, 3.55, 4.3, 3.9, 0.16, DARK, 0)
finish('shop_a')

box(0, 0, 1.5, 3.4, 3.4, 3.0, WHITE, 1)
box(0, -1.78, 0.9, 2.8, 0.1, 1.7, WOOD2, 0)                        # roll-up shutter
box(0, -1.86, 2.2, 3.6, 0.16, 0.6, GOLD, 0)
prism(0, 0, 3.0, 3.6, 3.6, 0.7, MAROON, 0)                         # pitched roof
finish('shop_b')

# --- bahay kubo: nominal 2.6 wide x 3.6 tall (one mesh, was 6 primitives) ---
for sx in (-0.95, 0.95):
    for sy in (-0.85, 0.85): cyl(sx, sy, 0.36, 0.1, 0.08, 0.72, 5, WOOD2, 0)
box(0, 0, 1.5, 2.4, 2.2, 1.5, NIPA, 0)
box(0, -1.12, 1.6, 0.9, 0.1, 0.7, WOOD2, 0)                        # window flap
box(0, -1.3, 1.95, 0.9, 0.36, 0.05, BAMBOO, 0, 0.0)
cone(0, 0, 2.25, 1.85, 1.5, 4, WOOD2, 0, math.pi/4)                # nipa roof
cone(0, 0, 3.05, 1.05, 0.75, 4, WOOD2, 0, math.pi/4)               # second layer
for i in range(4): box(0.62, -1.15 - i*0.16, 0.14 + i*0.2, 0.7, 0.08, 0.05, BAMBOO, 0)
finish('hut2')

# --- jeepney: nominal 5 long (x) ---
box(0, 0, 1.05, 5.0, 2.0, 1.1, WHITE, 1)                           # body
box(-0.3, 0, 1.95, 3.6, 1.9, 0.7, WHITE, 1)                        # cabin/roof
box(-0.3, 0, 2.36, 3.8, 2.0, 0.12, METAL, 0)                       # roof rack
box(1.9, 0, 1.85, 1.2, 1.8, 0.6, GLASS, 0)                         # windshield
for s in (-1, 1): box(-0.3, s*0.96, 1.95, 3.4, 0.06, 0.5, GLASS2, 0)
box(2.55, 0, 1.0, 0.3, 2.0, 0.5, METAL, 0)                         # bumper
for s in (-1, 1): box(2.4, s*0.7, 1.35, 0.16, 0.34, 0.28, LAMP, 0)
for a in (-1.5, 1.6):
    for s in (-1, 1): cyl(a, s*1.02, 0.42, 0.42, 0.42, 0.28, 8, TYRE, 0, math.pi/2)
box(0, 0, 0.5, 4.6, 1.7, 0.5, DARK, 0)
finish('jeep')

# --- small car: nominal 4 long ---
box(0, 0, 0.72, 4.0, 1.8, 0.66, WHITE, 1)
box(-0.15, 0, 1.32, 2.2, 1.66, 0.62, WHITE, 1)
box(-0.15, 0, 1.34, 2.05, 1.72, 0.5, GLASS, 0)
box(0, 0, 1.66, 1.9, 1.6, 0.06, WHITE, 1)
for s in (-1, 1): box(1.75, s*0.6, 0.86, 0.2, 0.36, 0.22, LAMP, 0)
box(-1.92, 0, 0.86, 0.14, 1.4, 0.16, RED, 0)
for a in (-1.28, 1.32):
    for s in (-1, 1): cyl(a, s*0.9, 0.36, 0.36, 0.36, 0.24, 8, TYRE, 0, math.pi/2)
finish('car2')

# --- street props ---
cyl(0, 0, 0.09, 0.2, 0.17, 0.18, 8, DARK, 0)
cyl(0, 0, 1.7, 0.075, 0.05, 3.2, 6, ASPH, 0)
box(0.32, 0, 3.32, 0.75, 0.1, 0.1, ASPH, 0)
box(0.62, 0, 3.2, 0.44, 0.26, 0.16, LAMP, 0)
finish('lamp2')

for s in (-0.7, 0.7): box(s, 0, 0.22, 0.1, 0.5, 0.44, ASPH, 0)
for i in range(4): box(0, -0.2 + i*0.14, 0.46, 1.7, 0.11, 0.06, WOOD, 0)
for i in range(3): box(0, 0.24, 0.6 + i*0.13, 1.7, 0.06, 0.1, WOOD, 0)
finish('bench')

box(0, 0, 0.26, 0.62, 0.62, 0.52, STONE, 0)
box(0, 0, 0.55, 0.68, 0.68, 0.08, STONE, 0)
cyl(0, 0, 0.74, 0.24, 0.2, 0.34, 7, LEAF2, 0)
cyl(0.1, 0.08, 0.9, 0.16, 0.13, 0.3, 6, LEAF, 0)
finish('planter')

cyl(0, 0, 0.42, 0.11, 0.09, 0.84, 8, MAROON, 0)
cyl(0, 0, 0.86, 0.13, 0.13, 0.06, 8, CREAM, 0)
finish('bollard')

for sx in (-1.5, 1.5):
    for sy in (-0.6, 0.6): cyl(sx, sy, 1.2, 0.06, 0.06, 2.4, 6, METAL, 0)
box(0, 0, 2.48, 3.4, 1.5, 0.14, MAROON, 0)
box(0, 0.66, 1.3, 3.2, 0.08, 1.9, GLASS2, 0)
box(0, 0.2, 0.5, 2.4, 0.4, 0.1, WOOD, 0)
for s in (-1, 1): box(s*1.05, 0.2, 0.24, 0.1, 0.4, 0.4, ASPH, 0)
finish('busstop')

for sx in (-1.1, 1.1):
    for sy in (-0.8, 0.8): cyl(sx, sy, 1.0, 0.05, 0.05, 2.0, 5, WOOD2, 0)
box(0, 0, 1.02, 2.4, 1.8, 0.1, WOOD, 0)                            # counter
prism(0, 0, 2.0, 2.7, 2.1, 0.55, MAROON, 0)                        # tarp roof
for i in range(3): box(-0.7 + i*0.7, -0.2, 1.18, 0.42, 0.42, 0.24, GOLD, 0)
finish('stall')

# --- nature: one mesh each (palm was 7 separate meshes in the world) ---
cyl(0, 0, 2.5, 0.3, 0.17, 5.0, 6, TRUNK, 0)
for i in range(7):
    a = i/7.0*TAU
    box(math.cos(a)*1.5, math.sin(a)*1.5, 5.05 - abs(math.cos(a*1.7))*0.15,
        3.0, 0.42, 0.07, PALM if i % 2 else LEAF2, 0, a)
for i in range(3):
    a = i/3.0*TAU + 0.5
    cyl(math.cos(a)*0.28, math.sin(a)*0.28, 4.86, 0.13, 0.11, 0.26, 6, WOOD2, 0)
finish('palm2')

cyl(0, 0, 0.95, 0.32, 0.22, 1.9, 6, TRUNK, 0)
cyl(0.22, 0.12, 1.7, 0.12, 0.08, 0.9, 5, TRUNK, 0, 0.4)
for c, r, z in ((LEAF, 1.35, 2.5), (LEAF2, 1.05, 3.3), (LEAF, 0.7, 3.9)):
    cyl(0, 0, z, r, r*0.78, 0.8, 7, c, 0)
finish('tree2')

# --- calibration chip: known colour, lets me confirm the exporter did not shift values ---
box(0, 0, 0.05, 0.1, 0.1, 0.1, (0.5, 0.25, 0.75), 0)
finish('cal', ao=False)

# =====================================================================================
for o in bpy.context.scene.objects: o.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_apply=False,
                          export_materials='NONE', export_vertex_color='ACTIVE',
                          export_active_vertex_color_when_no_material=True,
                          export_normals=True, export_texcoords=False,
                          export_yup=True, use_selection=False)
import os
print('DONE %s %d objects %d bytes' % (OUT, len(bpy.context.scene.objects), os.path.getsize(OUT)))
