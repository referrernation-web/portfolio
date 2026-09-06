# Blender headless: GLB -> FBX for Mixamo (mesh + baked texture, no armature). run: blender -b -P blend_fbx.py -- in.glb out.fbx
import bpy, sys, os
argv=sys.argv[sys.argv.index('--')+1:]; IN,OUT=argv[0],argv[1]
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=IN)
for o in list(bpy.context.scene.objects):
    if o.type!='MESH': bpy.data.objects.remove(o)
obj=[o for o in bpy.context.scene.objects if o.type=='MESH'][0]; obj.parent=None
bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True); bpy.context.view_layer.objects.active=obj
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
# write the texture next to the fbx so Mixamo picks it up (it accepts a zip with fbx + textures)
for img in bpy.data.images:
    if img.has_data and img.name!='Render Result':
        img.filepath_raw=os.path.join(os.path.dirname(OUT),'dianna_diffuse.png'); img.file_format='PNG'; img.save()
bpy.ops.export_scene.fbx(filepath=OUT,use_selection=True,apply_scale_options='FBX_SCALE_ALL',path_mode='COPY',embed_textures=True,mesh_smooth_type='FACE')
print('DONE',OUT,os.path.getsize(OUT))
