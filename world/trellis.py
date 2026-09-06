"""Image -> textured GLB via microsoft/TRELLIS.2 (ZeroGPU). usage: python trellis.py <image> <out.glb> [resolution 512|1024|1536] [seed]"""
import sys, os, shutil, time, json, httpx
from gradio_client import Client, handle_file
img,out=sys.argv[1],sys.argv[2]; res_=sys.argv[3] if len(sys.argv)>3 else "1024"; seed=float(sys.argv[4]) if len(sys.argv)>4 else 0
tok=None; tp=os.path.expanduser('~/.hf-token')
if os.path.exists(tp): tok=open(tp).read().strip() or None
t0=time.time()
c=Client("microsoft/TRELLIS.2",token=tok,verbose=False,httpx_kwargs={"timeout":httpx.Timeout(1800,connect=60)})
api=c.view_api(return_format="dict",print_info=False)
ep=api["named_endpoints"]["/image_to_3d"]; params=ep["parameters"]
print("image_to_3d params:",[(p["parameter_name"],p.get("parameter_default")) for p in params])
c.predict(api_name="/start_session")
pre=c.predict(input=handle_file(img),api_name="/preprocess_image")
print("preprocessed:",str(pre)[:120])
kw={}
for p in params:
    n=p["parameter_name"]; d=p.get("parameter_default")
    if n=="image": kw[n]=handle_file(pre["path"] if isinstance(pre,dict) else pre)
    elif n=="seed": kw[n]=seed
    elif n=="resolution": kw[n]=res_
    else: kw[n]=d
r=c.predict(**kw,api_name="/image_to_3d"); print("image_to_3d:",str(r)[:200],"t",round(time.time()-t0))
g=c.predict(decimation_target=60000,texture_size=2048,api_name="/extract_glb"); print("extract:",str(g)[:300])
paths=[x for x in (g if isinstance(g,(list,tuple)) else [g]) if isinstance(x,str) and x.lower().endswith(".glb")]
if paths:
    best=max(paths,key=lambda p:os.path.getsize(p)); shutil.copy(best,out); print("saved",out,os.path.getsize(out),"in",round(time.time()-t0),"s")
else: print("NO GLB",g)
