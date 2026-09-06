"""Image -> textured GLB via the free Hunyuan3D-2.1 Hugging Face Space (ZeroGPU).
usage: python gen3d.py <image> <out.glb> [steps] [octree]
Token: optional, read from ~/.hf-token if present (raises the ZeroGPU quota).
"""
import os, sys, shutil, time, json
from gradio_client import Client, handle_file

img, out = sys.argv[1], sys.argv[2]
steps = float(sys.argv[3]) if len(sys.argv) > 3 else 30
octree = float(sys.argv[4]) if len(sys.argv) > 4 else 256
tok = None
tp = os.path.expanduser('~/.hf-token')
if os.path.exists(tp):
    tok = open(tp).read().strip() or None
t0 = time.time()
import httpx
from PIL import Image
im = Image.open(img).convert("RGB"); im.thumbnail((768, 768)); small = os.path.join(os.path.dirname(os.path.abspath(out)), "_in.png"); im.save(small)
img = small
c = Client("tencent/Hunyuan3D-2.1", token=tok, verbose=False, httpx_kwargs={"timeout": httpx.Timeout(900.0, connect=60.0)})
try:
    c.predict(value="Turbo", api_name="/on_gen_mode_change")
    c.predict(value="Low", api_name="/on_decode_mode_change")
except Exception as e:
    print("mode set skipped:", str(e)[:120])
res = c.predict(image=handle_file(img), mv_image_front=None, mv_image_back=None, mv_image_left=None, mv_image_right=None,
                steps=steps, guidance_scale=5.0, seed=1234, octree_resolution=octree, check_box_rembg=True,
                api_name="/generation_all")
print("result:", json.dumps(res, default=str)[:800])
paths = []
def walk(v):
    if isinstance(v, str) and v.lower().endswith(('.glb', '.obj')): paths.append(v)
    elif isinstance(v, dict):
        for x in v.values(): walk(x)
    elif isinstance(v, (list, tuple)):
        for x in v: walk(x)
walk(res)
glbs = [p for p in paths if p.lower().endswith('.glb')]
print("files:", paths)
if glbs:
    # the textured one is usually the last/largest
    best = max(glbs, key=lambda p: os.path.getsize(p) if os.path.exists(p) else 0)
    shutil.copy(best, out)
    print("saved", out, os.path.getsize(out), "bytes in", round(time.time() - t0), "s")
else:
    print("NO GLB in result")
