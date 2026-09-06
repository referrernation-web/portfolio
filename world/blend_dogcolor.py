# Blender headless: keep the Rodin texture everywhere, but project the official render onto the FACE region (hero
# texture) and bake back onto the model's own UVs (so the UniRig result can reuse the texture via swaptex.js).
# run: blender -b -P blend_face.py -- in.glb out.glb out_texture.png
import bpy, sys, numpy as np
from mathutils import Vector
argv=sys.argv[sys.argv.index('--')+1:]; IN,OUT,TEXOUT,REF=argv[0],argv[1],argv[2],argv[3]
M='C:/Users/DELL/AppData/Local/Temp/claude/C--Users-DELL-Desktop/4879bca3-2969-4557-8e5f-72e02e23c64c/scratchpad/mascots/'
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=IN)
obj=[o for o in bpy.context.scene.objects if o.type=='MESH'][0]
for o in list(bpy.context.scene.objects):
    if o.type!='MESH': bpy.data.objects.remove(o)
obj.parent=None; bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active=obj; obj.select_set(True)
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
base_img=None
for mat in obj.data.materials:   # the image wired into Base Color (not the normal/roughness maps)
    if mat and mat.use_nodes:
        for nd in mat.node_tree.nodes:
            if nd.type=='BSDF_PRINCIPLED':
                for l in mat.node_tree.links:
                    if l.to_node==nd and l.to_socket.name=='Base Color' and l.from_node.type=='TEX_IMAGE': base_img=l.from_node.image
        if base_img is None:
            for nd in mat.node_tree.nodes:
                if nd.type=='TEX_IMAGE' and nd.image and 'normal' not in nd.image.name.lower() and 'rough' not in nd.image.name.lower(): base_img=nd.image
print('BASE', base_img.name if base_img else None, [i.name for i in bpy.data.images])
assert base_img, 'no base texture'
vs=np.array([v.co[:] for v in obj.data.vertices]); lo=vs.min(0); sz=vs.max(0)-lo; n=(vs-lo)/sz
emp=bpy.data.objects.new('box',None); bpy.context.scene.collection.objects.link(emp); emp.location=Vector(lo); emp.scale=Vector(sz)
# glTF +z (front, verified by screenshot) -> Blender -Y ; across = X ; up = Z
W,H=604,755; box=(109,4,497,754)
mat=bpy.data.materials.new('face'); mat.use_nodes=True; nt=mat.node_tree; nd=nt.nodes; ln=nt.links
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
uvn=node('ShaderNodeUVMap'); base=node('ShaderNodeTexImage',image=base_img); ln.new(uvn.outputs[0],base.inputs['Vector'])
tc=node('ShaderNodeTexCoord',object=emp); sep=node('ShaderNodeSeparateXYZ'); ln.new(tc.outputs['Object'],sep.inputs[0])
geo=node('ShaderNodeNewGeometry'); nsep=node('ShaderNodeSeparateXYZ'); ln.new(geo.outputs['Normal'],nsep.inputs[0])
X,Y,Z=sep.outputs['X'],sep.outputs['Y'],sep.outputs['Z']; NF=m('MULTIPLY',nsep.outputs['Y'],-1.0)

# colour grade by region: head (front 30%, upper half) -> lighter silver-grey and desaturated; body stays dark
Fc=m('SUBTRACT',1.0,Y)
front=m('MULTIPLY',m('SUBTRACT',Fc,.62),6.0,clamp=True); up=m('MULTIPLY',m('SUBTRACT',Z,.42),6.0,clamp=True); headm=m('MULTIPLY',front,up)
bw=node('ShaderNodeRGBToBW'); ln.new(base.outputs['Color'],bw.inputs[0])
grey=node('ShaderNodeMix',data_type='RGBA'); grey.inputs[0].default_value=.6; ln.new(base.outputs['Color'],grey.inputs[6]); ln.new(bw.outputs[0],grey.inputs[7])   # desaturate
gain=m('ADD',1.0,m('MULTIPLY',headm,0.9))   # up to x1.9 on the head
brightK=node('ShaderNodeMix',data_type='RGBA',blend_type='MULTIPLY'); brightK.inputs[0].default_value=1.0; ln.new(grey.outputs[2],brightK.inputs[6]); comb3=node('ShaderNodeCombineColor'); ln.new(gain,comb3.inputs[0]); ln.new(gain,comb3.inputs[1]); ln.new(gain,comb3.inputs[2]); ln.new(comb3.outputs[0],brightK.inputs[7])
lift=node('ShaderNodeMix',data_type='RGBA',blend_type='ADD'); ln.new(headm,lift.inputs[0]); ln.new(brightK.outputs[2],lift.inputs[6]); silver=node('ShaderNodeRGB'); silver.outputs[0].default_value=(.03,.03,.033,1); ln.new(silver.outputs[0],lift.inputs[7])
mix=node('ShaderNodeMix',data_type='RGBA'); mix.inputs[0].default_value=1.0; ln.new(lift.outputs[2],mix.inputs[6]); ln.new(lift.outputs[2],mix.inputs[7])
emis=node('ShaderNodeEmission'); ln.new(mix.outputs[2],emis.inputs['Color']); out=node('ShaderNodeOutputMaterial'); ln.new(emis.outputs[0],out.inputs['Surface'])
obj.data.materials.clear(); obj.data.materials.append(mat)
bake=bpy.data.images.new('face_bake',2048,2048); bn=node('ShaderNodeTexImage',image=bake); nt.nodes.active=bn
sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.samples=4; sc.cycles.device='CPU'; sc.render.bake.margin=8
bpy.ops.object.bake(type='EMIT'); bake.filepath_raw=TEXOUT; bake.file_format='PNG'; bake.save()
fin=bpy.data.materials.new('dianna'); fin.use_nodes=True; fn=fin.node_tree; bsdf=fn.nodes['Principled BSDF']; bsdf.inputs['Roughness'].default_value=.85; bsdf.inputs['Metallic'].default_value=0
ti=fn.nodes.new('ShaderNodeTexImage'); ti.image=bake; fn.links.new(ti.outputs['Color'],bsdf.inputs['Base Color'])
obj.data.materials.clear(); obj.data.materials.append(fin); bpy.data.objects.remove(emp)
bpy.ops.export_scene.gltf(filepath=OUT,export_format='GLB',export_image_format='JPEG',export_jpeg_quality=88,export_apply=False)
print('DONE verts=%d'%len(obj.data.vertices))
