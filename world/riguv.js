// Add projected UVs + the fur atlas to the UniRig skinned mesh (keeps JOINTS/WEIGHTS). node riguv.js in.glb out.glb
const path=require('path');const G='C:/Users/DELL/AppData/Local/Temp/claude/C--Users-DELL-Desktop/4879bca3-2969-4557-8e5f-72e02e23c64c/scratchpad/gt/node_modules/';
const {NodeIO}=require(G+'@gltf-transform/core');const {unweld}=require(G+'@gltf-transform/functions');const fs=require('fs');
(async()=>{const io=new NodeIO();const doc=await io.read(process.argv[2]);await doc.transform(unweld());
const prim=doc.getRoot().listMeshes()[0].listPrimitives()[0];const P=prim.getAttribute('POSITION').getArray();const n=P.length/3;
let mn=[1e9,1e9,1e9],mx=[-1e9,-1e9,-1e9];for(let i=0;i<n;i++)for(let k=0;k<3;k++){mn[k]=Math.min(mn[k],P[i*3+k]);mx[k]=Math.max(mx[k],P[i*3+k])}
const sz=mx.map((v,k)=>v-mn[k]),cen=mn.map((v,k)=>v+sz[k]/2);
const W0=341,W1=512,W2=512,AW=1365,H=512,FH=512,LH=291,RH=349;const uv=new Float32Array(n*2);let sign=0;const N=[];
for(let f=0;f<n;f+=3){const a=[P[f*3],P[f*3+1],P[f*3+2]],b=[P[f*3+3],P[f*3+4],P[f*3+5]],c=[P[f*3+6],P[f*3+7],P[f*3+8]];
 const e1=[b[0]-a[0],b[1]-a[1],b[2]-a[2]],e2=[c[0]-a[0],c[1]-a[1],c[2]-a[2]];const nx=e1[1]*e2[2]-e1[2]*e2[1],ny=e1[2]*e2[0]-e1[0]*e2[2],nz=e1[0]*e2[1]-e1[1]*e2[0];
 const l=Math.hypot(nx,ny,nz)||1;const cx=(a[0]+b[0]+c[0])/3-cen[0],cy=(a[1]+b[1]+c[1])/3-cen[1],cz=(a[2]+b[2]+c[2])/3-cen[2];sign+=(nx*cx+ny*cy+nz*cz)/l;N.push([nx/l,ny/l,nz/l])}
const s=sign<0?-1:1;
for(let f=0;f<n;f+=3){const fn=N[f/3].map(v=>v*s);const front=fn[2]>.35,left=!front&&fn[0]>=0;
 for(let j=0;j<3;j++){const i=f+j;const x=(P[i*3]-mn[0])/sz[0],y=(P[i*3+1]-mn[1])/sz[1],z=(P[i*3+2]-mn[2])/sz[2];let u,v;
  if(front){u=x*W0/AW;v=(1-y)*FH/H}else if(left){u=(W0+(1-z)*W1)/AW;v=(1-y)*LH/H}else{u=(W0+W1+z*W2)/AW;v=(1-y)*RH/H}uv[i*2]=u;uv[i*2+1]=v}}
const buf=doc.getRoot().listBuffers()[0];const acc=doc.createAccessor('uv').setType('VEC2').setArray(uv).setBuffer(buf);prim.setAttribute('TEXCOORD_0',acc);
const col=prim.getAttribute('COLOR_0');if(col){prim.setAttribute('COLOR_0',null);col.dispose()}
const tex=doc.createTexture('fur').setImage(fs.readFileSync('tex/kimpoy-atlas.jpg')).setMimeType('image/jpeg');
let mat=prim.getMaterial();if(!mat){mat=doc.createMaterial('fur');prim.setMaterial(mat)}mat.setBaseColorTexture(tex).setBaseColorFactor([1,1,1,1]).setMetallicFactor(0).setRoughnessFactor(1);
await io.write(process.argv[3],doc);console.log('wrote',process.argv[3],fs.statSync(process.argv[3]).size,'verts',n,'sign',s)})().catch(e=>{console.error(e);process.exit(1)});
