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
    # sharp AI turnaround views (black dog) recoloured to Kimpoy's real mid-grey, projected by vertex normal
    def grey(p):
        I=img(p); lum=I[:,:,0]*.299+I[:,:,1]*.587+I[:,:,2]*.114
        lum=np.clip((lum-.5)*.75+.5,0,1); lum=np.clip(lum*1.25+.03,0,1); return np.stack([lum*1.0,lum*.99,lum*.96],2)  # real Kimpoy: dark grey, soft contrast
    F,L,Rr=grey('tex/proj-kimpoy-front.jpg'),grey('tex/proj-kimpoy-left.jpg'),grey('tex/proj-kimpoy-right.jpg')
    V=1-n[:,1]
    side=np.where(N[:,0:1]>=0, samp(L,1-n[:,2],V), samp(Rr,n[:,2],V))
    front=samp(F,n[:,0],V)
    w=np.clip((N[:,2]-.2)/.35,0,1)[:,None]; col=front*w+side*(1-w)
    col*= (0.62+0.38*(N[:,1:2]*.5+.5))                # cheap AO: undersides darker
    col*= np.where((n[:,1:2]>.55)&(n[:,2:3]>.6),1.22,1.0)  # lighter grey head like the real Kimpoy
    col*= 1+np.random.uniform(-.06,.06,(len(n),1))    # fur speckle
    col*=0.72                                         # overall: real Kimpoy reads dark grey in daylight
    print('mean lum',float((col[:,0]*.299+col[:,1]*.587+col[:,2]*.114).mean()))
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
