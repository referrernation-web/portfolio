// dump the base-colour texture of a GLB to a file: node gettex.js in.glb out.(png|jpg)
const G='C:/Users/DELL/AppData/Local/Temp/claude/C--Users-DELL-Desktop/4879bca3-2969-4557-8e5f-72e02e23c64c/scratchpad/gt/node_modules/';
const {NodeIO}=require(G+'@gltf-transform/core');const fs=require('fs');
(async()=>{const doc=await new NodeIO().read(process.argv[2]);const t=doc.getRoot().listMaterials()[0].getBaseColorTexture();fs.writeFileSync(process.argv[3],t.getImage());console.log('tex',t.getMimeType(),t.getImage().length)})();
