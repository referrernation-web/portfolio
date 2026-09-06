import bpy, sys, numpy as np
IN=sys.argv[sys.argv.index('--')+1]
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=IN)
obj=[o for o in bpy.context.scene.objects if o.type=='MESH'][0]
for o in list(bpy.context.scene.objects):
    if o.type!='MESH': bpy.data.objects.remove(o)
obj.parent=None; bpy.context.view_layer.objects.active=obj; obj.select_set(True)
obj.rotation_euler=(0,0,0.35); bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
vs=np.array([v.co[:] for v in obj.data.vertices]); lo=vs.min(0); sz=vs.max(0)-lo; n=(vs-lo)/sz
print('PROBE size',np.round(sz,2))
band=(n[:,2]>.45)&(n[:,2]<.75)   # mid height (Z up)
for ax,name in [(0,'X'),(1,'Y')]:
    lo_,hi_=n[band,ax].min(),n[band,ax].max(); print('PROBE band extent',name,round(lo_,2),round(hi_,2))
# arm tip = farthest-from-centre point in band
cx,cy=n[band,0].mean(),n[band,1].mean(); d=(n[band,0]-cx)**2+(n[band,1]-cy)**2; i=d.argmax(); print('PROBE arm tip (x,y) norm',round(n[band][i,0],2),round(n[band][i,1],2),'centre',round(cx,2),round(cy,2))
# head: top 20% - where is the face? hair drape: extent in x/y
top=n[:,2]>.8; print('PROBE head x',round(n[top,0].min(),2),round(n[top,0].max(),2),'y',round(n[top,1].min(),2),round(n[top,1].max(),2))
