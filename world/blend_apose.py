# Headless Blender: take the rigged Dianna, pose her into a clean A-pose, BAKE that pose into the
# mesh and export an unrigged FBX for Mixamo's auto-rigger. Mixamo silently fails on her Rodin rest
# pose because one arm is raised beside her head.
# run: blender -b -P blend_apose.py -- models/dianna-rig.glb mixamo/dianna-apose.fbx
import bpy, bmesh, sys, math
from mathutils import Vector, Quaternion

argv = sys.argv[sys.argv.index('--')+1:]
IN, OUT = argv[0], argv[1]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=IN)
obj = [o for o in bpy.context.scene.objects if o.type == 'MESH'][0]
arm = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE'][0]

# ---- weld the mesh: the Rodin/UniRig export is an unwelded triangle soup (3232 islands,
# 19546 non-manifold edges) and Mixamo's auto-rigger silently fails on it ----
def islands(bm):
    seen = set(); out = []
    bm.verts.ensure_lookup_table()
    for v in bm.verts:
        if v.index in seen: continue
        stack = [v]; comp = []; seen.add(v.index)
        while stack:
            c = stack.pop(); comp.append(c)
            for e in c.link_edges:
                o = e.other_vert(c)
                if o.index not in seen: seen.add(o.index); stack.append(o)
        out.append(comp)
    return out

bm = bmesh.new(); bm.from_mesh(obj.data)
print('before: %d verts, %d islands' % (len(bm.verts), len(islands(bm))))
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0008)
comps = sorted(islands(bm), key=len, reverse=True)
print('welded: %d verts, %d islands, biggest %d' % (len(bm.verts), len(comps), len(comps[0])))
keep = max(1, int(len(comps[0])*0.02))
dead = [v for c in comps[1:] if len(c) < keep for v in c]        # jacket cords, stray shards
if dead: bmesh.ops.delete(bm, geom=dead, context='VERTS')
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(obj.data); bm.free(); obj.data.update()
bm = bmesh.new(); bm.from_mesh(obj.data)
nm = sum(1 for e in bm.edges if not e.is_manifold)
print('after: %d verts, %d islands, %d non-manifold edges of %d' % (len(bm.verts), len(islands(bm)), nm, len(bm.edges)))
bm.free()

# ---- role detection, same idea as girlRoles() in the world: leaf-to-branch chains, arms are widest ----
def kids(b): return [c for c in b.children if c.name in arm.data.bones]
chains = []
for b in arm.data.bones:
    if kids(b): continue
    ch = [b]; c = b
    while c.parent and len(kids(c.parent)) == 1:
        c = c.parent; ch.insert(0, c)
    chains.append(ch)

def head_w(b): return arm.matrix_world @ b.head_local
bb_min = Vector((min(head_w(b).x for b in arm.data.bones), min(head_w(b).y for b in arm.data.bones), min(head_w(b).z for b in arm.data.bones)))
bb_max = Vector((max(head_w(b).x for b in arm.data.bones), max(head_w(b).y for b in arm.data.bones), max(head_w(b).z for b in arm.data.bones)))
span = bb_max - bb_min
def nx(b): return (head_w(b).x - bb_min.x)/span.x

legs = sorted(chains, key=lambda c: head_w(c[-1]).z)[:2]
rest = [c for c in chains if c not in legs]
arms = sorted(rest, key=lambda c: -abs(nx(c[-1]) - 0.5))[:2]
arms = sorted(arms, key=lambda c: nx(c[-1]))            # left first, right second
print('arms:', [[b.name for b in c] for c in arms])
print('legs:', [[b.name for b in c] for c in legs])

# ---- pose search: rotate each shoulder/elbow so the hand lands at an A-pose target ----
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
for pb in arm.pose.bones:
    pb.rotation_mode = 'QUATERNION'
    pb.rotation_quaternion = Quaternion((1, 0, 0, 0))
bpy.context.view_layer.update()

def pose_of(name): return arm.pose.bones[name]
def world_head(name):
    bpy.context.view_layer.update()
    return arm.matrix_world @ pose_of(name).head

AXES = [Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))]
def search(bone_name, target, coarse=0.35, fine=0.06):
    """greedy per-axis search for the rotation that puts the chain tip nearest `target`"""
    pb = pose_of(bone_name)
    best = pb.rotation_quaternion.copy()
    def score(q):
        pb.rotation_quaternion = q
        bpy.context.view_layer.update()
        return (world_tip() - target).length
    bestv = score(best)
    for step in (coarse, fine):
        improved = True
        while improved:
            improved = False
            for ax in AXES:
                for sgn in (1, -1):
                    cand = best @ Quaternion(ax, sgn*step)
                    v = score(cand)
                    if v < bestv - 1e-4:
                        bestv = v; best = cand; improved = True
    pb.rotation_quaternion = best
    bpy.context.view_layer.update()
    return bestv

for ch in arms:
    tipname = ch[-1].name
    def world_tip(_n=tipname): return world_head(_n)
    shoulder = ch[0].name
    sw = world_head(shoulder)
    side = 1.0 if (sw.x - (bb_min.x + span.x/2)) > 0 else -1.0
    reach = (world_head(tipname) - sw).length
    # near-T-pose: the puffer jacket is wide, so the arms have to clear it or Mixamo cannot find them
    target = sw + Vector((side*reach*0.95, -reach*0.05, -reach*0.30))
    d = search(shoulder, target)
    mid = ch[min(2, len(ch)-1)].name                       # elbow: straighten what is left
    def world_tip(_n=tipname): return world_head(_n)
    d2 = search(mid, target, 0.25, 0.05)
    print('%s -> target err %.3f then %.3f (reach %.2f)' % (shoulder, d, d2, reach))

bpy.ops.object.mode_set(mode='OBJECT')

# ---- bake the pose into the mesh, then drop the skeleton: Mixamo wants an unrigged mesh ----
bpy.context.view_layer.objects.active = obj
for m in obj.modifiers:
    if m.type == 'ARMATURE':
        bpy.ops.object.modifier_apply(modifier=m.name)
for vg in list(obj.vertex_groups): obj.vertex_groups.remove(vg)
obj.parent = None
bpy.data.objects.remove(arm)
bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

bpy.ops.export_scene.fbx(filepath=OUT, use_selection=True, object_types={'MESH'},
                         add_leaf_bones=False, path_mode='COPY', embed_textures=True,
                         mesh_smooth_type='FACE', bake_space_transform=False)
import os
print('DONE %s %d bytes, %d verts' % (OUT, os.path.getsize(OUT), len(obj.data.vertices)))
