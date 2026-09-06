"""Bake photo-projected vertex colours into the AI shapes (no UVs) -> models/kimpoy.glb, models/dianna.glb
usage: python bake.py kimpoy|dianna"""
import sys, numpy as np, trimesh
from PIL import Image
from scipy.ndimage import distance_transform_edt as edt
M='C:/Users/DELL/AppData/Local/Temp/claude/C--Users-DELL-Desktop/4879bca3-2969-4557-8e5f-72e02e23c64c/scratchpad/mascots/'
def img(p):  return np.asarray(Image.open(p).convert('RGB')).astype(np.float32)/255
def fillbg(p, alpha=None, thr=205):
    im=Image.open(p).convert('RGBA'); a=np.asarray(im).astype(np.int16)
    bg=(a[:,:,3]<40) if im.getextrema()[3][0]<255 else ((a[:,:,:3].min(2)>thr)&((a[:,:,:3].max(2)-a[:,:,:3].min(2))<20))
    ys,xs=np.where(~bg); box=(xs.min(),ys.min(),xs.max()+1,ys.max()+1)
    idx=edt(bg,return_distances=False,return_indices=True); f=a[idx[0],idx[1]][:,:,:3]
    return f.astype(np.float32)/255, box
def samp(I,U,V):
    h,w=I.shape[:2]; ix=np.clip((U*w).astype(int),0,w-1); iy=np.clip((V*h).astype(int),0,h-1); return I[iy,ix]
def load(fn,roty=0.0):
    sc=trimesh.load(fn,force='scene'); m=list(sc.geometry.values())[0]
    m=trimesh.Trimesh(vertices=m.vertices.copy(),faces=m.faces.copy(),process=False)
    if roty: m.apply_transform(trimesh.transformations.rotation_matrix(roty,[0,1,0]))
    v=m.vertices; lo=v.min(0); sz=v.max(0)-lo; return m,(v-lo)/sz,np.asarray(m.vertex_normals)
which=sys.argv[1]
if which=='kimpoy':
    m,n,N=load('models/kimpoy-mv.glb',0.0)           # nose already +z (verified by screenshot)
    face=img(M+'kimpoy-face-real.jpg'); fur=img(M+'kimpoy-fur-tile.jpg')
    # fur everywhere: pseudo-triplanar tile, body a bit darker than the head (real Kimpoy: grey head, darker body)
    U=np.mod(n[:,0]*1.4+n[:,2]*2.2,1.0); V=np.mod(n[:,1]*1.8+n[:,2]*.3,1.0); col=samp(fur,U,V)
    shade=np.where(n[:,1]>.55,0.5,0.36)+np.random.uniform(-.04,.04,len(n)); col=np.clip((col-.5)*1.3+.5,0,1)*shade[:,None]  # real Kimpoy is mid-grey: darken the (over-lit) video fur
    # face: head-front vertices, ellipse inside the head box (x .05-.95, y .5-1) -> real face photo
    hx=(n[:,0]-.05)/.9; hy=(n[:,1]-.5)/.5
    head=(n[:,1]>.5)&(n[:,2]>.55)&(N[:,2]>.2)
    e=((hx-.5)**2/.5**2+((1-hy)-.55)**2/.5**2)
    sel=head&(e<1)
    fc=samp(face,hx,1-hy); w=np.clip((1-e)*2,0,1)[:,None]; fc=np.clip((fc-.5)*1.2+.5,0,1)*.72; col[sel]=fc[sel]*w[sel]+col[sel]*(1-w[sel])
else:
    m,n,N=load('models/dianna-s.glb',0.35)              # arms -> +z (verified)
    F,box=fillbg(M+'diana-render.png')
    U=n[:,0]; V=1-n[:,1]; U=box[0]/F.shape[1]+U*(box[2]-box[0])/F.shape[1]; V=box[1]/F.shape[0]+V*(box[3]-box[1])/F.shape[0]
    col=samp(F,U,V)
    back_head=(N[:,2]<-.15)&(n[:,1]>.72)           # back of the head: hair, not a mirrored face
    hairU=np.full(len(n),0.17)+np.random.uniform(-.03,.03,len(n)); col[back_head]=samp(F,hairU,V)[back_head]
    top=(N[:,1]>.6)&(n[:,1]>.9); col[top]=samp(F,hairU,np.full(len(n),0.12))[top]
col=np.clip(col,0,1)**2.2   # three.js r128 treats COLOR_0 as linear; bake sRGB->linear so the photo colours render as seen
m.visual=trimesh.visual.ColorVisuals(m,vertex_colors=np.clip(np.concatenate([col,np.ones((len(col),1))],1)*255,0,255).astype(np.uint8))
out='models/%s-baked.glb'%which; m.export(out); import os; print(out,os.path.getsize(out),'verts',len(n))
