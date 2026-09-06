# RGBA photo tiles (background -> alpha 0) + a seamless dark fur tile from the real video crop
import numpy as np
from PIL import Image, ImageOps
from scipy.ndimage import binary_erosion, gaussian_filter
M='C:/Users/DELL/AppData/Local/Temp/claude/C--Users-DELL-Desktop/4879bca3-2969-4557-8e5f-72e02e23c64c/scratchpad/mascots/'
def grey(I):
    I=np.asarray(I.convert('RGB')).astype(np.float32)/255; lum=I[:,:,0]*.299+I[:,:,1]*.587+I[:,:,2]*.114
    lum=np.clip((lum-.5)*.8+.5,0,1); lum=np.clip(lum*.78+.02,0,1); return np.stack([lum,lum*.99,lum*.96],2)
for v in ['front','left','right']:
    src=Image.open(M+'kimpoy-%s.png'%v).convert('RGB'); a=np.asarray(src).astype(np.int16)
    bg=(a.min(2)>200)&((a.max(2)-a.min(2))<22)
    ys,xs=np.where(~bg); box=(xs.min(),ys.min(),xs.max()+1,ys.max()+1)
    g=grey(src)[box[1]:box[3],box[0]:box[2]]; al=(~bg)[box[1]:box[3],box[0]:box[2]]
    al=gaussian_filter(binary_erosion(al,iterations=4).astype(np.float32),2)
    rgba=np.dstack([g,al]); im=Image.fromarray((rgba*255).astype(np.uint8),'RGBA'); im.thumbnail((1024,1024)); im.save('tex/kimpoy-%s-rgba.png'%v); print(v,im.size)
fur=Image.open(M+'kimpoy-fur-tile.jpg').convert('RGB'); f=np.asarray(fur).astype(np.float32)/255
lum=f[:,:,0]*.299+f[:,:,1]*.587+f[:,:,2]*.114; lum=np.clip((lum-lum.mean())*1.1+.30,0,1); g=np.stack([lum,lum*.99,lum*.96],2)
t=Image.fromarray((g*255).astype(np.uint8)); w,h=t.size; big=Image.new('RGB',(w*2,h*2))
big.paste(t,(0,0)); big.paste(ImageOps.mirror(t),(w,0)); big.paste(ImageOps.flip(t),(0,h)); big.paste(ImageOps.flip(ImageOps.mirror(t)),(w,h)); big.save('tex/kimpoy-fur-seamless.jpg',quality=88); print('fur',big.size,'mean',round(float(lum.mean()),2))
