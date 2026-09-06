"""Texture the AI shapes with a projected UV atlas: per-face region (front/back/side tiles), vertices unwelded at
region seams so no triangle streaks. usage: python uvbake.py dianna|kimpoy -> models/<name>-uv.glb + tex/<name>-atlas.jpg"""
import sys, os, numpy as np, trimesh
from PIL import Image
from scipy.ndimage import distance_transform_edt as edt
M='C:/Users/DELL/AppData/Local/Temp/claude/C--Users-DELL-Desktop/4879bca3-2969-4557-8e5f-72e02e23c64c/scratchpad/mascots/'
def fillbg_rgba(p):
    im=Image.open(p).convert('RGBA'); a=np.asarray(im).astype(np.int16)
    bg=a[:,:,3]<40; ys,xs=np.where(~bg); box=(xs.min(),ys.min(),xs.max()+1,ys.max()+1)
    idx=edt(bg,return_distances=False,return_indices=True); return a[idx[0],idx[1]][:,:,:3].astype(np.uint8), box
def load(fn,roty):
    sc=trimesh.load(fn,force='scene'); m=list(sc.geometry.values())[0]
    m=trimesh.Trimesh(vertices=m.vertices.copy(),faces=m.faces.copy(),process=False)
    if roty: m.apply_transform(trimesh.transformations.rotation_matrix(roty,[0,1,0]))
    m.unmerge_vertices()                       # every face owns its 3 vertices -> hard seams instead of streaks
    v=m.vertices; lo=v.min(0); sz=v.max(0)-lo; n=(v-lo)/sz
    fn_=np.asarray(m.face_normals); cen=m.triangles_center; radial=cen-v.mean(0)
    if (np.einsum('ij,ij->i',fn_,radial).mean()<0): fn_=-fn_     # make face normals point outward regardless of winding
    N=np.repeat(fn_,3,axis=0)                  # per-vertex = its face's normal (faces are [i,i+1,i+2] after unmerge)
    return m,n,N
which=sys.argv[1]
if which=='dianna':
    m,n,N=load('models/dianna-s.glb',0.35)      # arms -> +z (verified in three.js)
    F,box=fillbg_rgba(M+'diana-render.png'); H,W=F.shape[:2]
    B=F.copy(); hair=F[60:200,150:215]; B[60:200,215:300]=np.hstack([hair,hair])[:, :85]   # back tile: hair over the face
    skin=np.zeros((H,W//4,3),np.uint8); skin[:]=(214,168,150)
    atlas=np.hstack([F,B,skin]); AW=atlas.shape[1]
    fr=(n[:,1]>.8)&(n[:,1]<.95)&(N[:,2]>.3); hc=n[fr,0].mean(); print('mesh face centre x',round(hc,3),'verts',fr.sum())
    FACE_CX=255/W                                   # render: face centre column
    Uimg=FACE_CX+(n[:,0]-hc)*(box[2]-box[0])/W; Vimg=(box[1]+(1-n[:,1])*(box[3]-box[1]))/H   # align the mesh face to the render face
    back=N[:,2]<-.05
    u=np.where(back,(W+(1-Uimg)*W)/AW,Uimg*W/AW)
    arm=(n[:,2]>.6)&(n[:,1]>.42)&(n[:,1]<.78)          # sleeves reach forward: sample the render's sleeve, not the face
    u[arm]=(400+(n[arm,2]-.6)/.4*70)/AW; Vimg[arm]=(310+(n[arm,1]-.42)/.36*90)/H
    side=(np.abs(N[:,0])>.6)&(~arm)                     # side-facing faces would streak: tile a clean patch instead
    sb=side&(n[:,1]<.78); u[sb]=(300+np.mod(n[sb,2]*2.2,1)*140)/AW; Vimg[sb]=(250+np.mod(n[sb,1]*2.5,1)*190)/H    # puffer patch
    sh=side&(n[:,1]>=.78); u[sh]=(135+np.mod(n[sh,2]*1.5,1)*60)/AW; Vimg[sh]=(70+(1-(n[sh,1]-.78)/.22)*220)/H      # hair patch
    hand=(n[:,2]>.86)&(n[:,1]>.42)&(n[:,1]<.78); u[hand]=(2*W+W/8)/AW; Vimg=np.where(hand,.5,Vimg)
    uv=np.stack([u,1-Vimg],1); out='dianna'
else:
    m,n,N=load('models/kimpoy-mv.glb',0.0)      # nose -> +z
    def grey(p):
        I=np.asarray(Image.open(p).convert('RGB')).astype(np.float32)/255; lum=I[:,:,0]*.299+I[:,:,1]*.587+I[:,:,2]*.114
        lum=np.clip((lum-.5)*.8+.5,0,1); lum=np.clip(lum*.78+.02,0,1); return (np.stack([lum,lum*.99,lum*.96],2)*255).astype(np.uint8)
    F,L,Rr=[grey('tex/proj-kimpoy-%s.jpg'%k) for k in ('front','left','right')]
    h=max(F.shape[0],L.shape[0],Rr.shape[0])
    def pad(I):
        o=np.zeros((h,I.shape[1],3),np.uint8); o[:]=I[-1].mean(0).astype(np.uint8); o[:I.shape[0]]=I; return o
    F,L,Rr=pad(F),pad(L),pad(Rr); atlas=np.hstack([F,L,Rr]); AW=atlas.shape[1]; W0,W1,W2=F.shape[1],L.shape[1],Rr.shape[1]
    front=N[:,2]>.35; left=(~front)&(N[:,0]>=0)
    u=np.where(front,n[:,0]*W0/AW,np.where(left,(W0+(1-n[:,2])*W1)/AW,(W0+W1+n[:,2]*W2)/AW))
    v=np.where(front,(1-n[:,1])*F.shape[0]/h,np.where(left,(1-n[:,1])*L.shape[0]/h,(1-n[:,1])*Rr.shape[0]/h))
    uv=np.stack([u,1-v],1); out='kimpoy'
Image.fromarray(atlas).save('tex/%s-atlas.jpg'%out,quality=90)
m.visual=trimesh.visual.TextureVisuals(uv=uv,image=Image.open('tex/%s-atlas.jpg'%out))
m.export('models/%s-uv.glb'%out); print('models/%s-uv.glb'%out,os.path.getsize('models/%s-uv.glb'%out),'atlas',atlas.shape,'faces',len(m.faces))
