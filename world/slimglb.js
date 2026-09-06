// keep only the base-colour texture (as JPEG) : node slimglb.js in.glb out.glb
const G='C:/Users/DELL/AppData/Local/Temp/claude/C--Users-DELL-Desktop/4879bca3-2969-4557-8e5f-72e02e23c64c/scratchpad/gt/node_modules/';
const {NodeIO}=require(G+'@gltf-transform/core');const {textureCompress,prune}=require(G+'@gltf-transform/functions');const sharp=(()=>{try{return require(G+'sharp')}catch(e){return null}})();const fs=require('fs');
(async()=>{const io=new NodeIO();const doc=await io.read(process.argv[2]);
for(const mat of doc.getRoot().listMaterials()){mat.setNormalTexture(null);mat.setMetallicRoughnessTexture(null);mat.setOcclusionTexture(null);mat.setEmissiveTexture(null);mat.setRoughnessFactor(.85);mat.setMetallicFactor(0)}
await doc.transform(prune());
if(sharp){await doc.transform(textureCompress({encoder:sharp,targetFormat:'jpeg',quality:88}))}
await io.write(process.argv[3],doc);console.log('wrote',process.argv[3],fs.statSync(process.argv[3]).size,'sharp:',!!sharp)})().catch(e=>{console.error(e);process.exit(1)});
