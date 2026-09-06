"""Auto-rig a GLB with UniRig (HF Space jasongzy/UniRig): python rig.py in.glb out.glb"""
import sys, shutil, os, httpx, time
from gradio_client import Client, handle_file
t0=time.time()
c=Client("jasongzy/UniRig",verbose=False,httpx_kwargs={"timeout":httpx.Timeout(1800,connect=60)})
res=c.predict(input_path=handle_file(sys.argv[1]),output_format="glb",api_name="/process_pipeline")
print("result:",res)
p=res if isinstance(res,str) else (res.get("path") if isinstance(res,dict) else None)
if p and os.path.exists(p): shutil.copy(p,sys.argv[2]); print("saved",sys.argv[2],os.path.getsize(sys.argv[2]),"in",round(time.time()-t0),"s")
