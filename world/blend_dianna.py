# Blender headless: smooth the AI shape, Smart-UV it, bake a normal-blended projection of the Pragmata render
# (front image, hair-covered back, tiled puffer/hair patches on the sides, skin on the hands) into a 2K texture.
# run: blender -b -P blend_dianna.py -- <in.glb> <out.glb>
import bpy, sys, math, numpy as np
from mathutils import Vector
argv=sys.argv[sys.argv.index('--')+1:]; IN,OUT=argv[0],argv[1]
M='C:/Users/DELL/AppData/Local/Temp/claude/C--Users-DELL-Desktop/4879bca3-2969-4557-8e5f-72e02e23c64c/scratchpad/mascots/'
ATLAS='C:/Users/DELL/Desktop/FOLDER/mark-portfolio/world/tex/dianna-atlas.jpg'   # front | back(hair over face) | skin
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=IN)
obj=[o for o in bpy.context.scene.objects if o.type=='MESH'][0]
for o in list(bpy.context.scene.objects):
    if o.type!='MESH': bpy.data.objects.remove(o)   # drop the glTF root empty so bake/export see only the mesh
obj.parent=None; bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active=obj; obj.select_set(True)
obj.rotation_euler=(0,0,0.35)     # three.js rotateY(.35) == Blender rotate Z (arms -> forward)
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
# 1) take the AI noise off the surface
mod=obj.modifiers.new('sm','SMOOTH'); mod.factor=.6; mod.iterations=6; bpy.ops.object.modifier_apply(modifier='sm')
# clean topology: voxel remesh, then decimate to ~30k faces (the AI mesh is noisy and over-dense)
dim=max(obj.dimensions); rm=obj.modifiers.new('rm','REMESH'); rm.mode='VOXEL'; rm.voxel_size=dim/140; rm.use_smooth_shade=True; bpy.ops.object.modifier_apply(modifier='rm')
dc=obj.modifiers.new('dc','DECIMATE'); dc.ratio=min(1.0,30000/max(1,len(obj.data.polygons))); bpy.ops.object.modifier_apply(modifier='dc')
mod=obj.modifiers.new('sm2','SMOOTH'); mod.factor=.4; mod.iterations=3; bpy.ops.object.modifier_apply(modifier='sm2')
bpy.ops.object.shade_smooth()
# 2) proper UVs
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(80),island_margin=0.01,area_weight=0.5); bpy.ops.object.mode_set(mode='OBJECT')
# 3) projection material (Object coords normalised by an empty sized to the bbox)
vs=np.array([v.co[:] for v in obj.data.vertices]); lo=vs.min(0); sz=vs.max(0)-lo
emp=bpy.data.objects.new('box',None); bpy.context.scene.collection.objects.link(emp); emp.location=Vector(lo); emp.scale=Vector(sz)
n=(vs-lo)/sz
# Blender: up=Z, forward(three +z)=-Y. mesh face centre x for aligning to the render face column
front_v=(n[:,0]<.3)&(n[:,2]>.8)&(n[:,2]<.95); hc=float(n[front_v,1].mean()) if front_v.any() else .5   # PROBE: forward = -X, across = Y, up = Z
W,H=604,755; AW=1359; box=(109,4,497,754); FACE_CX=255/W; sx=(box[2]-box[0])/W; bh=(box[3]-box[1])/H
mat=bpy.data.materials.new('proj'); mat.use_nodes=True; nt=mat.node_tree; nd=nt.nodes; ln=nt.links
for x in list(nd): nd.remove(x)
def node(t,**kw):
    z=nd.new(t)
    for k,v in kw.items(): setattr(z,k,v)
    return z
img=bpy.data.images.load(ATLAS); img.colorspace_settings.name='sRGB'
tc=node('ShaderNodeTexCoord',object=emp); sep=node('ShaderNodeSeparateXYZ'); ln.new(tc.outputs['Object'],sep.inputs[0])
geo=node('ShaderNodeNewGeometry'); nsep=node('ShaderNodeSeparateXYZ'); ln.new(geo.outputs['Normal'],nsep.inputs[0])
def m(op,a,b=None,**kw):
    z=node('ShaderNodeMath',operation=op,use_clamp=kw.get('clamp',False))
    if isinstance(a,(int,float)): z.inputs[0].default_value=a
    else: ln.new(a,z.inputs[0])
    if b is not None:
        if isinstance(b,(int,float)): z.inputs[1].default_value=b
        else: ln.new(b,z.inputs[1])
    return z.outputs[0]
X,Y,Z=sep.outputs['X'],sep.outputs['Y'],sep.outputs['Z']; NX,NY,NZ=nsep.outputs['X'],nsep.outputs['Y'],nsep.outputs['Z']
def tex(u,v,tile_off,tile_w):   # sample the atlas tile: u,v in 0..1 of the tile
    comb=node('ShaderNodeCombineXYZ'); ln.new(m('ADD',m('MULTIPLY',u,tile_w/AW),tile_off/AW),comb.inputs[0]); ln.new(v,comb.inputs[1])
    t=node('ShaderNodeTexImage',image=img,extension='EXTEND'); ln.new(comb.outputs[0],t.inputs['Vector']); return t.outputs['Color']
# front image: u = FACE_CX + (x-hc)*sx ; v(bottom-up) = 1 - box1/H - (1-z)*bh
uF=m('ADD',m('MULTIPLY',m('SUBTRACT',Y,hc),sx),FACE_CX); vF=m('SUBTRACT',1-box[1]/H,m('MULTIPLY',m('SUBTRACT',1.0,Z),bh))
front=tex(uF,vF,0,W)
# back: clean puffer tile + hair (the render's zipper/belts must not mirror onto the back)
# side patches (tiled): puffer for the body, hair for the head
uP=m('FRACT',m('MULTIPLY',X,2.2)); vP=m('FRACT',m('MULTIPLY',Z,2.5)); puff=tex(m('ADD',m('MULTIPLY',uP,100/W),310/W),m('SUBTRACT',1-262/H,m('MULTIPLY',vP,135/H)),0,W)   # pure puffer area, no hand/belt edge
uH=m('FRACT',m('MULTIPLY',m('ADD',X,Y),1.2)); vH=m('SUBTRACT',1-70/H,m('MULTIPLY',m('FRACT',m('MULTIPLY',Z,3.0)),220/H)); hair=tex(m('ADD',m('MULTIPLY',uH,60/W),135/W),vH,0,W)
isHead=m('GREATER_THAN',Z,.78)
mixS=node('ShaderNodeMix',data_type='RGBA'); ln.new(isHead,mixS.inputs[0]); ln.new(puff,mixS.inputs[6]); ln.new(hair,mixS.inputs[7]); side=mixS.outputs[2]
# blend by normal: front (NY<-.15) / back (NY>.15) / side
fF=m('MULTIPLY',m('SUBTRACT',m('MULTIPLY',NX,-1.0),.25),2.0,clamp=True); fB=m('MULTIPLY',m('SUBTRACT',NX,.1),2.5,clamp=True)   # PROBE: front faces -X
mix1=node('ShaderNodeMix',data_type='RGBA'); ln.new(fF,mix1.inputs[0]); ln.new(side,mix1.inputs[6]); ln.new(front,mix1.inputs[7])
mix2=node('ShaderNodeMix',data_type='RGBA'); ln.new(fB,mix2.inputs[0]); ln.new(mix1.outputs[2],mix2.inputs[6]); ln.new(side,mix2.inputs[7])
# hands: forward-most 14% in the arm band -> skin
armZ=m('MULTIPLY',m('GREATER_THAN',Z,.5),m('LESS_THAN',Z,.86)); arm=m('MULTIPLY',m('LESS_THAN',X,.3),armZ)   # forward arms: sleeves, not the face projection
mixA=node('ShaderNodeMix',data_type='RGBA'); ln.new(arm,mixA.inputs[0]); ln.new(mix2.outputs[2],mixA.inputs[6]); ln.new(puff,mixA.inputs[7])
hand=m('MULTIPLY',m('LESS_THAN',X,.12),armZ)
skin=node('ShaderNodeRGB'); skin.outputs[0].default_value=(.66,.45,.38,1)
mix3=node('ShaderNodeMix',data_type='RGBA'); ln.new(hand,mix3.inputs[0]); ln.new(mixA.outputs[2],mix3.inputs[6]); ln.new(skin.outputs[0],mix3.inputs[7])
emis=node('ShaderNodeEmission'); ln.new(mix3.outputs[2],emis.inputs['Color']); out=node('ShaderNodeOutputMaterial'); ln.new(emis.outputs[0],out.inputs['Surface'])
obj.data.materials.clear(); obj.data.materials.append(mat)
# 4) bake emission -> 2K texture on the smart UVs
bake=bpy.data.images.new('dianna_tex',2048,2048); bnode=node('ShaderNodeTexImage',image=bake); nt.nodes.active=bnode
sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.samples=4; sc.cycles.device='CPU'; sc.render.bake.margin=8
bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True); bpy.context.view_layer.objects.active=obj
bpy.ops.object.bake(type='EMIT')
bake.filepath_raw='C:/Users/DELL/Desktop/FOLDER/mark-portfolio/world/tex/dianna-baked.png'; bake.file_format='PNG'; bake.save()
# 5) final material + export
fin=bpy.data.materials.new('dianna'); fin.use_nodes=True; fn=fin.node_tree; bsdf=fn.nodes['Principled BSDF']; bsdf.inputs['Roughness'].default_value=.9; bsdf.inputs['Metallic'].default_value=0
ti=fn.nodes.new('ShaderNodeTexImage'); ti.image=bake; fn.links.new(ti.outputs['Color'],bsdf.inputs['Base Color'])
obj.data.materials.clear(); obj.data.materials.append(fin)
bpy.data.objects.remove(emp)
bpy.ops.export_scene.gltf(filepath=OUT,export_format='GLB',export_image_format='JPEG',export_jpeg_quality=85,export_apply=True,use_selection=False)
print('DONE hc=%.3f verts=%d'%(hc,len(obj.data.vertices)))
