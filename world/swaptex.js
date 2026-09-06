// Replace the base-colour texture of a GLB with an image file (same UVs). node swaptex.js in.glb image.png out.glb
const G='C:/Users/DELL/AppData/Local/Temp/claude/C--Users-DELL-Desktop/4879bca3-2969-4557-8e5f-72e02e23c64c/scratchpad/gt/node_modules/';
const {NodeIO}=require(G+'@gltf-transform/core');const fs=require('fs');
(async()=>{const io=new NodeIO();const doc=await io.read(process.argv[2]);const img=fs.readFileSync(process.argv[3]);const mime=process.argv[3].toLowerCase().endsWith('.png')?'image/png':'image/jpeg';
let n=0;for(const mat of doc.getRoot().listMaterials()){let t=mat.getBaseColorTexture();if(!t){t=doc.createTexture('tex');mat.setBaseColorTexture(t)}t.setImage(img).setMimeType(mime);n++}
await io.write(process.argv[4],doc);console.log('swapped',n,'material(s) ->',process.argv[4],fs.statSync(process.argv[4]).size)})().catch(e=>{console.error(e);process.exit(1)});
