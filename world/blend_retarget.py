# Headless Blender: retarget Mixamo clips onto Dianna's UniRig skeleton and export one animated GLB.
# Mixamo's auto-rigger refuses her mesh (the puffer coat is as wide as she is tall, the rig job fails
# server-side with "Unknown error while generating motion"), so we take the clips on Mixamo's own
# default skeleton and copy the WORLD-SPACE rotation delta of each bone onto the matching UniRig bone
# - the same trick rotW() uses at runtime in index.html.
# run: blender -b -P blend_retarget.py -- models/dianna-rig.glb models/dianna-anim.glb "clip.fbx=sit" ...
import bpy, sys, math
from mathutils import Vector, Quaternion, Matrix

argv = sys.argv[sys.argv.index('--')+1:]
RIG, OUT, CLIPS = argv[0], argv[1], argv[2:]
STEP = 1

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=RIG)
dia = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE'][0]
dia.name = 'dianna'
mesh = [o for o in bpy.context.scene.objects if o.type == 'MESH'][0]

# ---- describe Dianna's skeleton by role (same logic as girlRoles() in the world) ----
def chains_of(arm):
    def kids(b): return [c for c in b.children if c.name in arm.data.bones]
    out = []
    for b in arm.data.bones:
        if kids(b): continue
        ch = [b]; c = b
        while c.parent and len(kids(c.parent)) == 1:
            c = c.parent; ch.insert(0, c)
        out.append(ch)
    return out

ch = chains_of(dia)
tip = lambda c: c[-1].head_local
legs = sorted(ch, key=lambda c: tip(c).z)[:2]
rest = [c for c in ch if c not in legs]
arms = sorted(rest, key=lambda c: -abs(tip(c).x))[:2]
head = sorted([c for c in rest if c not in arms], key=lambda c: -tip(c).z)[0]
arms = sorted(arms, key=lambda c: tip(c).x)          # -x first, +x second
legs = sorted(legs, key=lambda c: tip(c).x)
spine = []
b = head[0]
while b.parent: b = b.parent; spine.insert(0, b)     # root .. chest
spine.append(head[0])
print('spine', [b.name for b in spine])
print('head ', [b.name for b in head])
print('armL ', [b.name for b in arms[1]], ' armR', [b.name for b in arms[0]])
print('legL ', [b.name for b in legs[1]], ' legR', [b.name for b in legs[0]])

def pick(c, i): return c[min(i, len(c)-1)]
# Mixamo names -> Dianna bones. +x is treated as the character's left, matching Mixamo.
def build_map():
    m = {}
    sp = spine + [head[0]]
    names = ['mixamorig:Hips', 'mixamorig:Spine', 'mixamorig:Spine1', 'mixamorig:Spine2']
    for i, n in enumerate(names):
        if i < len(spine): m[n] = spine[i].name
    m['mixamorig:Neck'] = head[0].name
    if len(head) > 1: m['mixamorig:Head'] = head[1].name
    for side, arm in (('Left', arms[1]), ('Right', arms[0])):
        m['mixamorig:%sShoulder' % side] = pick(arm, 0).name
        m['mixamorig:%sArm' % side]      = pick(arm, 1).name
        m['mixamorig:%sForeArm' % side]  = pick(arm, 2).name
        m['mixamorig:%sHand' % side]     = pick(arm, 3).name
    for side, leg in (('Left', legs[1]), ('Right', legs[0])):
        m['mixamorig:%sUpLeg' % side] = pick(leg, 0).name
        m['mixamorig:%sLeg' % side]   = pick(leg, 1).name
        m['mixamorig:%sFoot' % side]  = pick(leg, 2).name
    return m

MAP = build_map()
print('map:', {k.replace('mixamorig:', ''): v for k, v in MAP.items()})

dia.animation_data_create()
actions = []

for spec in CLIPS:
    path, name = spec.rsplit('=', 1)
    upper = name.endswith(':upper'); name = name.replace(':upper', '')
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.fbx(filepath=path, ignore_leaf_bones=True, automatic_bone_orientation=False)
    new = [o for o in bpy.context.scene.objects if o not in before]
    src = [o for o in new if o.type == 'ARMATURE'][0]
    src_act = src.animation_data.action
    if not actions: base = src; base_f0 = int(src_act.frame_range[0])   # keep the first (seated) clip's rig around as the lower-body source
    f0, f1 = (int(src_act.frame_range[0]), int(src_act.frame_range[1]))
    f1 = min(f1, f0 + 300)                               # cap at 10 s; Sitting Talking runs 45 s
    # order parent-first so a child reads its parent's already-retargeted position
    order = [(s, d) for s, d in MAP.items() if s in src.pose.bones and d in dia.pose.bones]
    order.sort(key=lambda kv: len(src.pose.bones[kv[0]].parent_recursive))
    act = bpy.data.actions.new('dia_' + name)
    dia.animation_data.action = act
    for pb in dia.pose.bones: pb.rotation_mode = 'QUATERNION'
    nkeys = 0
    for f in range(f0, f1+1, STEP):
        bpy.context.scene.frame_set(f)
        for sname, dname in order:
            lower = any(k in sname for k in ('Hips', 'UpLeg', 'Leg', 'Foot'))
            if upper and lower:
                spb = base.pose.bones[sname]; sb = base.data.bones[sname]   # same frame of the seated idle: the legs keep breathing under the gesture
            else:
                spb = src.pose.bones[sname]; sb = src.data.bones[sname]
            dpb = dia.pose.bones[dname]
            delta = spb.matrix.to_quaternion() @ sb.matrix_local.to_quaternion().inverted()
            want  = delta @ dia.data.bones[dname].matrix_local.to_quaternion()
            loc = dpb.matrix.to_translation()
            dpb.matrix = Matrix.LocRotScale(loc, want, Vector((1.0, 1.0, 1.0)))
            bpy.context.view_layer.update()
        for sname, dname in order:
            dia.pose.bones[dname].keyframe_insert('rotation_quaternion', frame=f, group=dname)
            nkeys += 1
    act.use_fake_user = True
    actions.append(act)
    print('  %-22s frames %d..%d  keys %d -> action %s' % (name, f0, f1, nkeys, act.name))
    if src is not base:
        for o in new: bpy.data.objects.remove(o, do_unlink=True)

# glTF exports every action it can see, so drop the imported Mixamo originals or the file doubles
for o in [o for o in bpy.context.scene.objects if o not in (dia, mesh)]: bpy.data.objects.remove(o, do_unlink=True)
for a in list(bpy.data.actions):
    if a not in actions: bpy.data.actions.remove(a)
dia.animation_data.action = actions[0]
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_animations=True,
                          export_animation_mode='ACTIONS', export_nla_strips=False,
                          export_bake_animation=True, export_materials='EXPORT',
                          export_image_format='JPEG', use_selection=False)
import os
print('DONE %s %d bytes, %d actions: %s' % (OUT, os.path.getsize(OUT), len(actions), [a.name for a in actions]))
