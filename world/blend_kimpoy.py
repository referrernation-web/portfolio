# Blender headless: smooth the rigged Kimpoy (keeps UniRig skin weights), Smart-UV, bake a normal-blended projection
# of the 3 turnaround photos (alpha-matted so gaps become fur, not background) over a seamless dark fur tile, with AO.
# run: blender -b -P blend_kimpoy.py -- <in.glb> <out.glb>
import bpy, sys, math, numpy as np
from mathutils import Vector
argv=sys.argv[sys.argv.index('--')+1:]; IN,OUT=argv[0],argv[1]
T='C:/Users/DELL/Desktop/FOLDER/mark-portfolio/world/tex/'
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=IN)
obj=[o for o in bpy.context.scene.objects if o.type=='MESH'][0]; arm=[o for o in bpy.context.scene.objects if o.type=='ARMATURE'][0]
bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active=obj; obj.select_set(True)
# smooth the AI noise (vertex groups survive), no remesh (would drop the skin weights)
mod=obj.modifiers.new('sm','SMOOTH'); mod.factor=.5; mod.iterations=4; bpy.ops.object.modifier_apply(modifier='sm')
bpy.ops.object.shade_smooth()
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(80),island_margin=0.01,area_weight=0.5); bpy.ops.object.mode_set(mode='OBJECT')
# axes from the skeleton: forward = snout (bone_6) minus tail base (bone_31), in the mesh's frame
mw=obj.matrix_world.inverted()
def bpos(n): return mw@(arm.matrix_world@arm.data.bones[n].head_local)
fwd=(bpos('bone_6')-bpos('bone_31')); fwd.z=0; fwd.normalize()
Fax=0 if abs(fwd.x)>abs(fwd.y) else 1; Fsign=1 if fwd[Fax]>0 else -1; Aax=1-Fax
vs=np.array([v.co[:] for v in obj.data.vertices]); lo=vs.min(0); sz=vs.max(0)-lo
emp=bpy.data.objects.new('box',None); bpy.context.scene.collection.objects.link(emp); emp.location=Vector(lo); emp.scale=Vector(sz)
print('AXES forward',['X','Y'][Fax],Fsign,'across',['X','Y'][Aax])
mat=bpy.data.materials.new('proj'); mat.use_nodes=True; nt=mat.node_tree; nd=nt.nodes; ln=nt.links
for x in list(nd): nd.remove(x)
def node(t,**kw):
    z=nd.new(t)
    for k,v in kw.items(): setattr(z,k,v)
    return z
def m(op,a,b=None,clamp=False):
    z=node('ShaderNodeMath',operation=op,use_clamp=clamp)
    for i,v in enumerate((a,b)):
        if v is None: continue
        if isinstance(v,(int,float)): z.inputs[i].default_value=v
        else: ln.new(v,z.inputs[i])
    return z.outputs[0]
tc=node('ShaderNodeTexCoord',object=emp); sep=node('ShaderNodeSeparateXYZ'); ln.new(tc.outputs['Object'],sep.inputs[0])
geo=node('ShaderNodeNewGeometry'); nsep=node('ShaderNodeSeparateXYZ'); ln.new(geo.outputs['Normal'],nsep.inputs[0])
C=[sep.outputs['X'],sep.outputs['Y']]; N=[nsep.outputs['X'],nsep.outputs['Y']]; Z=sep.outputs['Z']
Fc=C[Fax] if Fsign>0 else m('SUBTRACT',1.0,C[Fax])          # 0 = tail end, 1 = nose
Ac=C[Aax]; NF=N[Fax] if Fsign>0 else m('MULTIPLY',N[Fax],-1.0); NA=N[Aax]
def img(p):
    i=bpy.data.images.load(p); i.colorspace_settings.name='sRGB'; return i
def tex(im,u,v,ext='EXTEND'):
    comb=node('ShaderNodeCombineXYZ'); ln.new(u,comb.inputs[0]); ln.new(v,comb.inputs[1])
    t=node('ShaderNodeTexImage',image=im,extension=ext); ln.new(comb.outputs[0],t.inputs['Vector']); return t
front=tex(img(T+'kimpoy-front-rgba.png'),Ac,Z)                          # front photo: across -> u, up -> v
left=tex(img(T+'kimpoy-left-rgba.png'),m('SUBTRACT',1.0,Fc),Z)         # nose at the left edge of the photo
right=tex(img(T+'kimpoy-right-rgba.png'),Fc,Z)                          # nose at the right edge
fur=tex(img(T+'kimpoy-fur-seamless.jpg'),m('FRACT',m('MULTIPLY',m('ADD',Ac,Fc),1.6)),m('FRACT',m('MULTIPLY',Z,1.8)),'REPEAT')
wF=m('MULTIPLY',m('SUBTRACT',NF,.15),2.0,clamp=True); wL=m('MULTIPLY',m('SUBTRACT',NA,.1),2.0,clamp=True); wR=m('MULTIPLY',m('SUBTRACT',m('MULTIPLY',NA,-1.0),.1),2.0,clamp=True)
def mixc(fac,a,b):
    z=node('ShaderNodeMix',data_type='RGBA'); ln.new(fac,z.inputs[0]); ln.new(a,z.inputs[6]); ln.new(b,z.inputs[7]); return z.outputs[2]
col=fur.outputs['Color']
col=mixc(m('MULTIPLY',wL,left.outputs['Alpha']),col,left.outputs['Color'])
col=mixc(m('MULTIPLY',wR,right.outputs['Alpha']),col,right.outputs['Color'])
col=mixc(m('MULTIPLY',wF,front.outputs['Alpha']),col,front.outputs['Color'])
ao=node('ShaderNodeAmbientOcclusion',samples=8); ao.inputs['Distance'].default_value=0.25
aof=m('ADD',m('MULTIPLY',ao.outputs['AO'],.55),.45)
mul=node('ShaderNodeMix',data_type='RGBA',blend_type='MULTIPLY'); mul.inputs[0].default_value=1.0; ln.new(col,mul.inputs[6]); ln.new(aof,mul.inputs[7])
emis=node('ShaderNodeEmission'); ln.new(mul.outputs[2],emis.inputs['Color']); out=node('ShaderNodeOutputMaterial'); ln.new(emis.outputs[0],out.inputs['Surface'])
obj.data.materials.clear(); obj.data.materials.append(mat)
bake=bpy.data.images.new('kimpoy_tex',2048,2048); bnode=node('ShaderNodeTexImage',image=bake); nt.nodes.active=bnode
sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.samples=16; sc.cycles.device='CPU'; sc.render.bake.margin=8
bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True); bpy.context.view_layer.objects.active=obj
bpy.ops.object.bake(type='EMIT')
bake.filepath_raw=T+'kimpoy-baked.png'; bake.file_format='PNG'; bake.save()
fin=bpy.data.materials.new('kimpoy'); fin.use_nodes=True; fn=fin.node_tree; bsdf=fn.nodes['Principled BSDF']; bsdf.inputs['Roughness'].default_value=1.0; bsdf.inputs['Metallic'].default_value=0
ti=fn.nodes.new('ShaderNodeTexImage'); ti.image=bake; fn.links.new(ti.outputs['Color'],bsdf.inputs['Base Color'])
obj.data.materials.clear(); obj.data.materials.append(fin)
for ca in list(obj.data.color_attributes): obj.data.color_attributes.remove(ca)
bpy.data.objects.remove(emp)
bpy.ops.export_scene.gltf(filepath=OUT,export_format='GLB',export_image_format='JPEG',export_jpeg_quality=85,export_apply=False,export_skins=True,export_animations=False)
print('DONE verts=%d bones=%d'%(len(obj.data.vertices),len(arm.data.bones)))
