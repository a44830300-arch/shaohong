// 미리보기 PNG: node preview.js 입력.svg 출력.png  (연두 배경 + 흰 배경 나란히, 4배 크기)
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage({deviceScaleFactor:2});
let svg=fs.readFileSync(process.argv[2],'utf8').replace(/width="(\d+)" height="(\d+)"/,(m,w,h)=>`width="${w*4}" height="${h*4}"`);
await p.setContent(`<body style="margin:0"><div id="w" style="display:inline-flex;gap:20px;padding:10px;background:#cfe3d0">${svg}<div style="background:#fff">${svg}</div></div></body>`);
await (await p.$('#w')).screenshot({path:process.argv[3]});await b.close();})();
