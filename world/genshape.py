"""python genshape.py <image> <out.glb> [steps] [octree] [seed] [mode]  -> untextured shape via /shape_generation (works without HF token)"""
import sys, os, shutil, httpx
from gradio_client import Client, handle_file
img,out=sys.argv[1],sys.argv[2]; steps=float(sys.argv[3]) if len(sys.argv)>3 else 30; octree=float(sys.argv[4]) if len(sys.argv)>4 else 256
seed=float(sys.argv[5]) if len(sys.argv)>5 else 1234; mode=sys.argv[6] if len(sys.argv)>6 else "Standard"
c=Client("tencent/Hunyuan3D-2.1",verbose=False,httpx_kwargs={"timeout":httpx.Timeout(900.0,connect=60.0)})
try: c.predict(value=mode,api_name="/on_gen_mode_change"); c.predict(value="Low",api_name="/on_decode_mode_change")
except Exception as e: print("mode",str(e)[:100])
res=c.predict(image=handle_file(img),mv_image_front=None,mv_image_back=None,mv_image_left=None,mv_image_right=None,steps=steps,guidance_scale=7.5,seed=seed,octree_resolution=octree,check_box_rembg=True,api_name="/shape_generation")
paths=[]
def walk(v):
    if isinstance(v,str) and v.lower().endswith('.glb'): paths.append(v)
    elif isinstance(v,dict): [walk(x) for x in v.values()]
    elif isinstance(v,(list,tuple)): [walk(x) for x in v]
walk(res); print(paths)
if paths: shutil.copy(paths[0],out); print("saved",out,os.path.getsize(out))
