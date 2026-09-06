"""Hyper3D Rodin (free-trial key from blender-mcp) image(s) -> textured GLB. python rodin.py out.glb img1 [img2 ...]"""
import sys, time, json, os, requests
KEY=os.environ.get('RODIN_KEY','vibecoding'); out=sys.argv[1]; imgs=sys.argv[2:]
files=[("images",(f"{i:04d}"+os.path.splitext(p)[1],open(p,'rb').read())) for i,p in enumerate(imgs)]
files+=[("tier",(None,os.environ.get("RODIN_TIER","Sketch"))),("mesh_mode",(None,"Raw")),("texture_mode",(None,"high"))]
r=requests.post("https://hyperhuman.deemos.com/api/v2/rodin",headers={"Authorization":f"Bearer {KEY}"},files=files,timeout=120); d=r.json(); print("create:",json.dumps(d)[:400])
sub=d.get("jobs",{}).get("subscription_key"); uuid=d.get("uuid")
if not sub: sys.exit("no subscription key")
t0=time.time()
while True:
    s=requests.post("https://hyperhuman.deemos.com/api/v2/status",headers={"Authorization":f"Bearer {KEY}"},json={"subscription_key":sub},timeout=60).json()
    st=[j["status"] for j in s.get("jobs",[])]; print("status",st,round(time.time()-t0),"s")
    if st and all(x=="Done" for x in st): break
    if any(x in("Failed","Error") for x in st): sys.exit("job failed: "+json.dumps(s)[:300])
    time.sleep(10)
dl=requests.post("https://hyperhuman.deemos.com/api/v2/download",headers={"Authorization":f"Bearer {KEY}"},json={"task_uuid":uuid},timeout=60).json()
print("files:",[i["name"] for i in dl.get("list",[])])
for i in dl.get("list",[]):
    if i["name"].endswith(".glb"):
        g=requests.get(i["url"],timeout=300); open(out,'wb').write(g.content); print("saved",out,len(g.content)); break
